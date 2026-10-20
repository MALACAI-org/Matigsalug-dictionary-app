import 'dictionary.dart';

/// The main dictionary's `sn` is a scientific name; only student `sn` is
/// a numbered sense. A repeated part of speech can introduce a new derivation.
class EntrySection {
  EntrySection({this.sense, this.partOfSpeech, this.subentry});
  String? sense;
  String? partOfSpeech;
  String? subentry;
  final fields = <EntryField>[];
  final photos = <DictionaryPhoto>[];

  bool get hasContent =>
      fields.any((f) => !{'ps', 'ms', 'sn', 'se'}.contains(f.marker));
}

class EntrySections {
  EntrySections(DictionaryEntry entry, String Function(String) normalize) {
    EntrySection current = EntrySection();
    String? mainSense;
    void finish() {
      if (current.fields.isNotEmpty) sections.add(current);
      current = EntrySection(sense: mainSense);
    }

    for (final field in entry.fields) {
      final marker = field.marker;
      if (sections.isEmpty &&
          current.fields.isEmpty &&
          {'ph', 'pn', 'dc', 'ds', 'de'}.contains(marker) &&
          (entry.source == 'main' || marker == 'ph')) {
        preface.add(field);
        continue;
      }
      if (entry.source == 'main' && marker == 'ms') {
        finish();
        mainSense = field.text;
        current.sense = mainSense;
      } else if (marker == 'ps') {
        if (current.hasContent || current.partOfSpeech != null) finish();
        current.partOfSpeech = field.text;
      } else if (entry.source == 'student' && marker == 'sn') {
        if (current.hasContent) {
          final previousPOS = current.partOfSpeech;
          finish();
          current.partOfSpeech = previousPOS;
        }
        current.sense = field.text;
      } else if (entry.source == 'student' && marker == 'se') {
        finish();
        current.subentry = field.text;
      }
      current.fields.add(field);
    }
    finish();

    final meanings = sections
        .where(
          (s) => s.fields.any(
            (f) => f.marker == (entry.source == 'main' ? 'gl' : 'de'),
          ),
        )
        .toList();
    for (final photo in entry.photos) {
      final caption = normalize(photo.caption);
      final matches = sections.where((section) {
        final markers = entry.source == 'main'
            ? {'oi', 'va', 'vd1', 'vd2'}
            : {'de'};
        return section.fields.any(
          (f) =>
              markers.contains(f.marker) &&
              f.text
                  .split(RegExp(r'[;,/]'))
                  .any((word) => normalize(word) == caption),
        );
      }).toList();
      // Explicit inflected forms are more specific than the entry headword.
      // Root-named pictures illustrate the first/root definition.
      if (matches.length == 1) {
        matches.single.photos.add(photo);
      } else if (matches.isEmpty &&
          caption == normalize(entry.headword) &&
          meanings.isNotEmpty) {
        meanings.first.photos.add(photo);
      } else if (sections.length == 1) {
        sections.single.photos.add(photo);
      } else {
        unplacedPhotos.add(photo);
      }
    }
  }

  final preface = <EntryField>[];
  final sections = <EntrySection>[];
  final unplacedPhotos = <DictionaryPhoto>[];
}

bool isDetailedField(String source, String marker) => source == 'main'
    ? {
        'oc',
        'oa',
        'oz',
        'oi',
        'va',
        'vd1',
        'vd2',
        've',
        'pn',
        'sp',
        'sc',
        'ddp',
        'mo',
        'eg',
      }.contains(marker)
    : {'sd', 'ng', 'pdl', 'pdv'}.contains(marker);

String partOfSpeechLabel(String? code) {
  const names = {
    'n': 'Noun',
    'n-ct': 'Countable noun',
    'n-uc': 'Uncountable noun',
    'n-pl': 'Plural noun',
    'prop_n': 'Proper noun',
    'v': 'Verb',
    'vt': 'Transitive verb',
    'vi': 'Intransitive verb',
    'v-aux': 'Auxiliary verb',
    'adj': 'Adjective',
    'adv': 'Adverb',
    'pron': 'Pronoun',
    'poss_pron': 'Possessive pronoun',
    'conj': 'Conjunction',
    'prep': 'Preposition',
    'num': 'Number',
    'part': 'Particle',
    'lnk': 'Linker',
    'det': 'Determiner',
    'ij': 'Interjection',
    'phrase': 'Phrase',
  };
  if (code == null) return '';
  return code
      .split(',')
      .map((part) => names[part.trim()] ?? part.trim())
      .join(', ');
}

class MeaningRun {
  const MeaningRun(this.text, {this.emphasized = false});
  final String text;
  final bool emphasized;
}

class ReadingBlock {
  const ReadingBlock(this.kind, this.fields, [this.meaning = const []]);
  final String kind;
  final List<EntryField> fields;
  final List<MeaningRun> meaning;
}

/// Recreate the old reader's joined gloss and paired examples, while retaining
/// the complete, ordered fields for the detailed view.
List<ReadingBlock> normalBlocks(EntrySection section, String source) {
  final result = <ReadingBlock>[];
  var gloss = <MeaningRun>[];
  void finishGloss() {
    if (gloss.isNotEmpty) {
      result.add(ReadingBlock('meaning', const [], gloss));
      gloss = [];
    }
  }

  final example = source == 'main' ? 'ex' : 'xv';
  final translation = source == 'main' ? 'tr' : 'xe';
  for (final field in section.fields) {
    final marker = field.marker;
    if (isDetailedField(source, marker) ||
        {'ps', 'ms'}.contains(marker) ||
        (source == 'student' && {'sn', 'se'}.contains(marker))) {
      continue;
    }
    if (source == 'main' && {'gli', 'gl'}.contains(marker)) {
      if (marker == 'gli') finishGloss();
      gloss.add(MeaningRun(field.text, emphasized: marker == 'gl'));
      continue;
    }
    finishGloss();
    if (marker == translation &&
        result.isNotEmpty &&
        result.last.kind == 'example' &&
        result.last.fields.length == 1 &&
        result.last.fields.first.marker == example) {
      final previous = result.removeLast();
      result.add(ReadingBlock('example', [previous.fields.first, field]));
    } else {
      result.add(
        ReadingBlock(
          marker == example || marker == translation ? 'example' : 'field',
          [field],
        ),
      );
    }
  }
  finishGloss();
  return result;
}
