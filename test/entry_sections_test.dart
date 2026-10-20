import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:matigsalug_dictionary/dictionary.dart';
import 'package:matigsalug_dictionary/entry_sections.dart';

void main() {
  final data = parseDictionary(
    File('assets/dictionary.json').readAsStringSync(),
  );

  test(
    'grouping the complete dictionaries preserves every field and photo',
    () {
      for (final entry in data.entries) {
        final grouped = EntrySections(entry, data.normalize);
        expect(
          [...grouped.preface, ...grouped.sections.expand((s) => s.fields)],
          entry.fields,
          reason: entry.id,
        );
        expect(
          [
            ...grouped.sections.expand((s) => s.photos),
            ...grouped.unplacedPhotos,
          ],
          unorderedEquals(entry.photos),
          reason: entry.id,
        );
      }
    },
  );

  test(
    'baley photos belong to the noun and building verb, not the adjective',
    () {
      final entry = data.entries.firstWhere((e) => e.headword == 'baley₁');
      final sections = EntrySections(entry, data.normalize);
      expect(sections.sections.map((s) => s.partOfSpeech), ['n', 'v', 'adj']);
      expect(sections.sections.map((s) => s.photos.length), [2, 1, 0]);
      expect(sections.sections[1].photos.single.caption, 'egbebaley');
      expect(sections.unplacedPhotos, isEmpty);
      final verb = normalBlocks(sections.sections[1], 'main');
      expect(verb.first.meaning.map((r) => r.text), [
        'for someone',
        'to build a house',
      ]);
      expect(verb.first.meaning.map((r) => r.emphasized), [false, true]);
      expect(verb[1].kind, 'example');
      expect(verb[1].fields.map((f) => f.marker), ['ex', 'tr']);
      expect(
        verb.expand((b) => b.fields).any((f) => f.marker == 'oi'),
        isFalse,
      );
    },
  );

  test('scientific names are not senses; student numbers are senses', () {
    final dog = data.entries.firstWhere((e) => e.headword == 'asu');
    final main = EntrySections(dog, data.normalize);
    expect(main.sections.first.sense, '1');
    expect(
      main.sections.first.fields.any(
        (f) => f.marker == 'sn' && f.text == 'Canis familiaris',
      ),
      isTrue,
    );
    final house = data.entries.firstWhere(
      (e) => e.headword == 'house' && e.source == 'student',
    );
    final student = EntrySections(house, data.normalize);
    expect(student.sections.map((s) => s.sense), [
      '1',
      '2',
      '3',
      '4',
      '5',
      '6',
    ]);
    expect(student.sections.map((s) => s.partOfSpeech), [
      'n-ct',
      'vt',
      'vt',
      'n-ct',
      'n-ct',
      'n-ct',
    ]);
  });

  test('continued glosses stay together across hidden inflection fields', () {
    final entry = data.entries.firstWhere((e) => e.headword == 'teul');
    final section = EntrySections(entry, data.normalize).sections.single;
    final meaning = normalBlocks(section, 'main').first.meaning;
    expect(meaning.map((r) => r.text), [
      'for a dog',
      'to howl',
      'because its lonely or communicating others',
    ]);
  });

  test('a form shared by two senses leaves its photo unassigned', () {
    const photo = DictionaryPhoto(asset: 'unused', caption: 'form');
    const entry = DictionaryEntry(
      id: 'test',
      source: 'main',
      headword: 'root',
      language: 'Matigsalug',
      summary: '',
      fields: [
        EntryField('ps', '', 'v'),
        EntryField('oi', '', 'form'),
        EntryField('gl', '', 'first meaning'),
        EntryField('ps', '', 'v'),
        EntryField('oi', '', 'form'),
        EntryField('gl', '', 'another meaning'),
      ],
      photos: [photo],
    );
    final sections = EntrySections(entry, data.normalize);
    expect(sections.unplacedPhotos, [photo]);
    expect(sections.sections.every((s) => s.photos.isEmpty), isTrue);
  });

  test('exact links work in both languages without prefix matches', () {
    expect(
      data
          .exactMatches('wolf', language: SearchLanguage.english)
          .map((e) => e.headword),
      containsAll(['lubu', 'singgalung']),
    );
    expect(
      data.exactMatches('wolfish', language: SearchLanguage.english),
      isEmpty,
    );
    expect(
      data
          .exactMatches('BALÈY', language: SearchLanguage.matigsalug)
          .map((e) => e.headword),
      containsAll(['baley₁', 'baley₂']),
    );
    expect(
      data
          .exactMatches('dog', language: SearchLanguage.english)
          .map((e) => e.headword),
      containsAll(['asu', 'dog']),
    );
  });
}
