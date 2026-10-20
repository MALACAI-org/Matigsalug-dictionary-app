import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:matigsalug_dictionary/definition_text.dart';
import 'package:matigsalug_dictionary/dictionary.dart';
import 'package:matigsalug_dictionary/entry_photos.dart';
import 'package:matigsalug_dictionary/entry_reader.dart';
import 'package:matigsalug_dictionary/main.dart';

void main() {
  final data = parseDictionary(
    File('assets/dictionary.json').readAsStringSync(),
  );
  final baley = data.entries.firstWhere((e) => e.headword == 'baley₁');

  void size(WidgetTester tester, Size size) {
    tester.view.physicalSize = size;
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
  }

  for (final wide in [false, true]) {
    testWidgets('photos follow their definition with wide=$wide', (
      tester,
    ) async {
      size(tester, Size(wide ? 1100 : 390, 900));
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: EntryView(
              entry: baley,
              linguistic: false,
              data: data,
              onLinguisticChanged: (_) {},
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();
      final noun = find.byKey(ValueKey('sense-${baley.id}-0'));
      final meaning = find
          .descendant(of: noun, matching: find.byType(DefinitionText))
          .first;
      final photos = find.descendant(
        of: noun,
        matching: find.byType(EntryPhotos),
      );
      expect(tester.widget<EntryPhotos>(photos).photos.length, 2);
      if (wide) {
        expect(
          tester.getTopLeft(photos).dx,
          greaterThan(tester.getTopRight(meaning).dx),
        );
      } else {
        expect(
          tester.getTopLeft(photos).dy,
          greaterThanOrEqualTo(tester.getBottomLeft(meaning).dy),
        );
        expect(
          tester.getBottomLeft(photos).dy,
          lessThan(
            tester
                .getTopLeft(find.text('Meupiya ne egpitawen ka baley niyu.'))
                .dy,
          ),
        );
      }
      final verb = find.byKey(ValueKey('sense-${baley.id}-1'));
      final verbPhotos = find.descendant(
        of: verb,
        matching: find.byType(EntryPhotos),
      );
      expect(
        tester.widget<EntryPhotos>(verbPhotos).photos.single.caption,
        'egbebaley',
      );
      expect(find.text('Meaning context'), findsNothing);
      expect(find.text('Word form'), findsNothing);
      expect(tester.takeException(), isNull);
    });
  }

  testWidgets('detailed mode preserves individual fields and sense photos', (
    tester,
  ) async {
    size(tester, const Size(1100, 1800));
    var detailed = false;
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: StatefulBuilder(
            builder: (context, setState) => EntryView(
              entry: baley,
              linguistic: detailed,
              data: data,
              onLinguisticChanged: (value) => setState(() => detailed = value),
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const ValueKey('entry-linguistic-switch')));
    await tester.pumpAndSettle();
    expect(find.text('Meaning context'), findsOneWidget);
    expect(find.text('Word form'), findsWidgets);
    expect(find.text('Case frame'), findsOneWidget);
    final verb = find.byKey(ValueKey('sense-${baley.id}-1'));
    expect(
      tester
          .widget<EntryPhotos>(
            find.descendant(of: verb, matching: find.byType(EntryPhotos)),
          )
          .photos
          .single
          .caption,
      'egbebaley',
    );
    expect(tester.takeException(), isNull);
  });

  testWidgets(
    'wolf in a definition opens lubu and Back returns to the definition',
    (tester) async {
      size(tester, const Size(390, 844));
      const example = DictionaryEntry(
        id: 'example',
        source: 'main',
        headword: 'example',
        language: 'Matigsalug',
        summary: '',
        fields: [
          EntryField('ps', '', 'v'),
          EntryField('gli', '', 'for a wolf'),
          EntryField('gl', '', 'to howl'),
          EntryField('df', '', 'baley₁'),
        ],
      );
      await tester.pumpWidget(
        MaterialApp(
          home: EntryReader(
            entries: [example, baley],
            initialIndex: 0,
            linguistic: false,
            data: data,
            onLinguisticChanged: (_) {},
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.byTooltip('Look up for'), findsNothing);
      await tester.tap(find.byTooltip('Look up wolf'));
      await tester.pumpAndSettle();
      expect(find.text('Choose an entry for “wolf”'), findsOneWidget);
      final lubu = data.entries.firstWhere((e) => e.headword == 'lubu');
      await tester.tap(find.byKey(ValueKey('link-choice-${lubu.id}')));
      await tester.pumpAndSettle();
      expect(
        tester.widget<EntryView>(find.byType(EntryView)).entry.headword,
        'lubu',
      );
      await tester.pageBack();
      await tester.pumpAndSettle();
      expect(find.byTooltip('Look up wolf'), findsOneWidget);
      await tester.tap(find.byTooltip('Look up baley₁'));
      await tester.pumpAndSettle();
      expect(
        tester.widget<EntryView>(find.byType(EntryView)).entry.headword,
        'baley₁',
      );
      await tester.pageBack();
      await tester.pumpAndSettle();
      await tester.drag(find.byTooltip('Look up wolf'), const Offset(-320, 0));
      await tester.pumpAndSettle();
      expect(find.text('2 of 2'), findsOneWidget);
      expect(tester.takeException(), isNull);
    },
  );

  testWidgets(
    'ambiguous links offer choices and preserve the original search',
    (tester) async {
      size(tester, const Size(390, 844));
      await tester.pumpWidget(DictionaryApp(loader: () async => data));
      await tester.pumpAndSettle();
      await tester.enterText(find.byType(TextField), 'teul');
      await tester.pump(const Duration(milliseconds: 250));
      await tester.tap(find.widgetWithText(ListTile, 'teul'));
      await tester.pumpAndSettle();
      await tester.tap(find.byTooltip('Look up dog'));
      await tester.pumpAndSettle();
      expect(find.text('Choose an entry for “dog”'), findsOneWidget);
      final asu = data.entries.firstWhere((e) => e.headword == 'asu');
      await tester.tap(find.byKey(ValueKey('link-choice-${asu.id}')));
      await tester.pumpAndSettle();
      expect(
        tester.widget<EntryView>(find.byType(EntryView)).entry.headword,
        'asu',
      );
      await tester.pageBack();
      await tester.pumpAndSettle();
      expect(find.byTooltip('Look up dog'), findsOneWidget);
      await tester.pageBack();
      await tester.pumpAndSettle();
      expect(find.widgetWithText(TextField, 'teul'), findsOneWidget);
      expect(tester.takeException(), isNull);
    },
  );

  testWidgets('a narrow phone with large text keeps photos below definitions', (
    tester,
  ) async {
    size(tester, const Size(320, 700));
    tester.platformDispatcher.textScaleFactorTestValue = 1.8;
    addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
    await tester.pumpWidget(
      MaterialApp(
        home: EntryReader(
          entries: [baley],
          initialIndex: 0,
          linguistic: false,
          data: data,
          onLinguisticChanged: (_) {},
        ),
      ),
    );
    await tester.pumpAndSettle();
    expect(find.byKey(const ValueKey('sense-column-0')), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}
