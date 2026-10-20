import 'dart:convert';

enum SearchLanguage { both, matigsalug, english }

class DictionaryPhoto {
  const DictionaryPhoto({required this.asset, required this.caption});
  final String asset;
  final String caption;

  factory DictionaryPhoto.fromJson(Map<String, dynamic> json) {
    final asset = json['asset'] as String;
    if (!RegExp(r'^assets/photos/[0-9a-f]{64}\.webp$').hasMatch(asset)) {
      throw const FormatException('Invalid dictionary photo path');
    }
    return DictionaryPhoto(asset: asset, caption: json['caption'] as String);
  }
}

class EntryField {
  const EntryField(this.marker, this.label, this.text);
  final String marker;
  final String label;
  final String text;
  factory EntryField.fromJson(Map<String, dynamic> json) => EntryField(
    json['marker'] as String,
    json['label'] as String,
    json['text'] as String,
  );
}

class DictionaryEntry {
  const DictionaryEntry({
    required this.id,
    required this.source,
    required this.headword,
    required this.language,
    required this.summary,
    required this.fields,
    this.photos = const [],
  });
  final String id;
  final String source;
  final String headword;
  final String language;
  final String summary;
  final List<EntryField> fields;
  final List<DictionaryPhoto> photos;
  String get sourceLabel =>
      source == 'main' ? 'Main dictionary' : 'Student dictionary';
  factory DictionaryEntry.fromJson(Map<String, dynamic> json) =>
      DictionaryEntry(
        id: json['id'] as String,
        source: json['source'] as String,
        headword: json['headword'] as String,
        language: json['language'] as String,
        summary: json['summary'] as String,
        fields: (json['fields'] as List)
            .map((f) => EntryField.fromJson(f as Map<String, dynamic>))
            .toList(),
        photos: (json['photos'] as List? ?? [])
            .map((p) => DictionaryPhoto.fromJson(p as Map<String, dynamic>))
            .toList(),
      );
}

class SearchResults {
  const SearchResults(this.entries, this.total);
  final List<DictionaryEntry> entries;
  final int total;
}

class _IndexTerm {
  const _IndexTerm(this.term, this.ids);
  final String term;
  final List<int> ids;
}

/// No Flutter or operating-system dependencies: identical lookup on every target.
class DictionaryData {
  DictionaryData._(
    this.entries,
    this._indexes,
    this._replacements,
    this.attribution,
  );
  final List<DictionaryEntry> entries;
  final Map<String, List<_IndexTerm>> _indexes;
  final Map<String, String> _replacements;
  final Map<String, dynamic> attribution;
  late final List<String> _sortKeys = entries
      .map((e) => normalize(e.headword))
      .toList();

  factory DictionaryData.fromJson(Map<String, dynamic> json) {
    if (json['schemaVersion'] != 1) {
      throw const FormatException('Unsupported dictionary data version');
    }
    final entries = (json['entries'] as List)
        .map((e) => DictionaryEntry.fromJson(e as Map<String, dynamic>))
        .toList();
    final indexes = <String, List<_IndexTerm>>{};
    for (final language in ['matigsalug', 'english']) {
      final rows = (json['indexes'] as Map<String, dynamic>)[language] as List;
      final terms = rows
          .map(
            (row) => _IndexTerm(row[0] as String, (row[1] as List).cast<int>()),
          )
          .toList();
      for (var i = 0; i < terms.length; i++) {
        if (terms[i].ids.any((id) => id < 0 || id >= entries.length) ||
            (i > 0 && terms[i - 1].term.compareTo(terms[i].term) >= 0)) {
          throw const FormatException('Invalid dictionary search index');
        }
      }
      indexes[language] = terms;
    }
    return DictionaryData._(
      entries,
      indexes,
      Map<String, String>.from(json['searchReplacements'] as Map),
      Map<String, dynamic>.from(json['attribution'] as Map),
    );
  }

  String normalize(String text) => text.runes
      .map((r) {
        final c = String.fromCharCode(r);
        return _replacements[c] ?? c;
      })
      .join()
      .toLowerCase()
      .replaceAll(RegExp(r'[\u0300-\u036f]'), '')
      .replaceAll('’', "'")
      .replaceAll(RegExp(r'\s+'), ' ')
      .trim();

  /// Exact index terms only: inline links must never use prefix-search results.
  List<DictionaryEntry> exactMatches(
    String query, {
    required SearchLanguage language,
  }) {
    final needle = normalize(query);
    if (needle.isEmpty) return const [];
    final ids = <int>{};
    final languages = language == SearchLanguage.both
        ? ['matigsalug', 'english']
        : [language.name];
    for (final key in languages) {
      final index = _indexes[key]!;
      var lo = 0;
      var hi = index.length;
      while (lo < hi) {
        final mid = (lo + hi) ~/ 2;
        if (index[mid].term.compareTo(needle) < 0) {
          lo = mid + 1;
        } else {
          hi = mid;
        }
      }
      if (lo < index.length && index[lo].term == needle) {
        ids.addAll(index[lo].ids);
      }
    }
    final matches = ids.map((id) => entries[id]).toList();
    matches.sort((a, b) {
      final directA = normalize(a.headword) == needle ? 0 : 1;
      final directB = normalize(b.headword) == needle ? 0 : 1;
      final rank = directA.compareTo(directB);
      return rank != 0 ? rank : a.headword.compareTo(b.headword);
    });
    return matches;
  }

  SearchResults search(
    String query, {
    SearchLanguage language = SearchLanguage.both,
    Set<String> sources = const {'main', 'student'},
    int limit = 100,
  }) {
    final needle = normalize(query);
    final ranks = <int, int>{};
    if (needle.isEmpty) {
      for (var i = 0; i < entries.length; i++) {
        final entry = entries[i];
        if (sources.contains(entry.source) &&
            (language == SearchLanguage.both ||
                entry.language.toLowerCase() == language.name)) {
          ranks[i] = 0;
        }
      }
    } else {
      final languages = language == SearchLanguage.both
          ? ['matigsalug', 'english']
          : [language.name];
      for (final key in languages) {
        final index = _indexes[key]!;
        // Lower-bound lookup avoids scanning every dictionary record per keypress.
        var lo = 0;
        var hi = index.length;
        while (lo < hi) {
          final mid = (lo + hi) ~/ 2;
          if (index[mid].term.compareTo(needle) < 0) {
            lo = mid + 1;
          } else {
            hi = mid;
          }
        }
        for (
          var i = lo;
          i < index.length && index[i].term.startsWith(needle);
          i++
        ) {
          final rank = index[i].term == needle ? 0 : 1;
          for (final id in index[i].ids) {
            if (sources.contains(entries[id].source) &&
                rank < (ranks[id] ?? 2)) {
              ranks[id] = rank;
            }
          }
        }
      }
    }
    final ids = ranks.keys.toList()
      ..sort((a, b) {
        final rank = ranks[a]!.compareTo(ranks[b]!);
        if (rank != 0) return rank;
        final word = _sortKeys[a].compareTo(_sortKeys[b]);
        return word != 0 ? word : entries[a].id.compareTo(entries[b].id);
      });
    return SearchResults(
      ids.take(limit).map((id) => entries[id]).toList(),
      ids.length,
    );
  }
}

DictionaryData parseDictionary(String source) =>
    DictionaryData.fromJson(jsonDecode(source) as Map<String, dynamic>);
