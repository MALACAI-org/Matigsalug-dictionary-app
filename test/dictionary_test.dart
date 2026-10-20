import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:matigsalug_dictionary/dictionary.dart';

void main() {
  late DictionaryData data;
  setUp(
    () => data = parseDictionary(
      File('test/fixtures/dictionary.json').readAsStringSync(),
    ),
  );

  test(
    'preserves homonyms, exact matches and prefix matches without duplicates',
    () {
      final results = data.search('a', language: SearchLanguage.matigsalug);
      expect(results.entries.map((e) => e.headword), ['a', 'a₂']);
      expect(data.search('ad').entries.single.headword, 'a');
      expect(data.search('  ABAND ').entries.single.headword, 'abandon');
    },
  );

  test('respects opposite dictionary directions and source filters', () {
    expect(data.search('abandon', language: SearchLanguage.english).total, 1);
    expect(
      data.search('abandon', language: SearchLanguage.matigsalug).total,
      0,
    );
    expect(
      data
          .search('engkeran', language: SearchLanguage.matigsalug)
          .entries
          .single
          .headword,
      'abandon',
    );
    expect(data.search('engkeran', sources: {'main'}).total, 0);
    expect(
      data.search('', language: SearchLanguage.english).entries.single.headword,
      'abandon',
    );
    expect(data.search('a', sources: {}).total, 0);
  });

  test(
    'normalizes accents and decomposed Unicode with the converter rules',
    () {
      expect(data.normalize('  BÀLÉY  '), 'baley');
      expect(data.normalize('BALE\u0300Y'), 'baley');
      expect(data.normalize('Æ ’'), "ae '");
      expect(data.search('à', language: SearchLanguage.matigsalug).total, 2);
    },
  );

  test('reports total separately from paginated results', () {
    final first = data.search('', limit: 1);
    expect(first.total, 3);
    expect(first.entries.length, 1);
    expect(data.search('', limit: 3).entries.take(1), first.entries);
    expect(data.search('zzzz').total, 0);
  });

  test('rejects incompatible schemas and dangling index references', () {
    final source = jsonDecode(
      File('test/fixtures/dictionary.json').readAsStringSync(),
    ) as Map<String, dynamic>;
    source['schemaVersion'] = 99;
    expect(() => DictionaryData.fromJson(source), throwsFormatException);
    source['schemaVersion'] = 1;
    source['indexes']['matigsalug'][0][1] = [1000];
    expect(() => DictionaryData.fromJson(source), throwsFormatException);
  });

  test('bundled real dictionary loads and supports both directions', () {
    final bundled = parseDictionary(
      File('assets/dictionary.json').readAsStringSync(),
    );
    expect(bundled.entries.length, greaterThan(10000));
    expect(
      bundled
          .search('baley', language: SearchLanguage.matigsalug)
          .entries
          .map((e) => e.headword),
      containsAll(['baley₁', 'baley₂']),
    );
    expect(
      bundled.search('house', language: SearchLanguage.english).entries,
      isNotEmpty,
    );
    expect(bundled.entries.any((e) => e.headword.startsWith('~')), isFalse);
    expect(
      bundled.entries.map((e) => e.id).toSet().length,
      bundled.entries.length,
    );
    final photos = bundled.entries
        .expand((e) => e.photos)
        .map((p) => p.asset)
        .toSet();
    expect(photos, isNotEmpty);
    expect(photos.every((asset) => File(asset).existsSync()), isTrue);
  });
}
