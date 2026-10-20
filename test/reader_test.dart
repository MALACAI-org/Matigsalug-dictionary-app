import 'dart:convert';
import 'dart:io';
import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:matigsalug_dictionary/about_dictionary.dart';
import 'package:matigsalug_dictionary/dictionary.dart';
import 'package:matigsalug_dictionary/dictionary_style.dart';
import 'package:matigsalug_dictionary/entry_reader.dart';
import 'package:matigsalug_dictionary/entry_photos.dart';
import 'package:matigsalug_dictionary/main.dart';

void main() {
  late DictionaryData data;
  setUp(() {
    final json = jsonDecode(
      File('test/fixtures/dictionary.json').readAsStringSync(),
    ) as Map<String, dynamic>;
    (json['entries'][0]['fields'] as List).insert(0, {
      'marker': 'oc',
      'label': 'Case frame',
      'text': 'agent',
    });
    data = DictionaryData.fromJson(json);
  });

  Future<void> openApp(
    WidgetTester tester, {
    DictionaryData? dictionary,
  }) async {
    tester.view.physicalSize = const Size(390, 844);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(
      DictionaryApp(loader: () async => dictionary ?? data),
    );
    await tester.pumpAndSettle();
  }

  testWidgets(
    'swipes step through filtered results and keep the search on return',
    (tester) async {
      await openApp(tester);
      await tester.enterText(find.byType(TextField), 'a');
      await tester.pump(const Duration(milliseconds: 250));
      await tester.tap(find.widgetWithText(ChoiceChip, 'Matigsalug'));
      await tester.pumpAndSettle();
      await tester.tap(find.byType(ListTile).first);
      await tester.pumpAndSettle();
      expect(find.text('1 of 2'), findsOneWidget);
      expect(
        tester
            .widget<IconButton>(
              find.byWidgetPredicate(
                (w) => w is IconButton && w.tooltip == 'Previous entry',
              ),
            )
            .onPressed,
        isNull,
      );
      await tester.drag(
        find.byKey(const ValueKey('entry-pages')),
        const Offset(-320, 0),
      );
      await tester.pumpAndSettle();
      expect(find.text('2 of 2'), findsOneWidget);
      expect(
        tester
            .widget<IconButton>(
              find.byWidgetPredicate(
                (w) => w is IconButton && w.tooltip == 'Next entry',
              ),
            )
            .onPressed,
        isNull,
      );
      await tester.drag(
        find.byKey(const ValueKey('entry-pages')),
        const Offset(320, 0),
      );
      await tester.pumpAndSettle();
      expect(find.text('1 of 2'), findsOneWidget);
      await tester.pageBack();
      await tester.pumpAndSettle();
      expect(find.widgetWithText(TextField, 'a'), findsOneWidget);
      expect(find.text('Results · 2 entries'), findsOneWidget);
    },
  );

  testWidgets(
    'entry toggle immediately shows technical fields and carries to next entry',
    (tester) async {
      await openApp(tester);
      await tester.tap(find.byType(ListTile).first);
      await tester.pumpAndSettle();
      expect(find.text('Case frame'), findsNothing);
      await tester.tap(find.byKey(const ValueKey('entry-linguistic-switch')));
      await tester.pumpAndSettle();
      expect(find.text('Case frame'), findsOneWidget);
      expect(find.text('agent'), findsOneWidget);
      await tester.tap(find.byTooltip('Next entry'));
      await tester.pumpAndSettle();
      expect(
        tester
            .widget<SwitchListTile>(
              find
                  .byKey(const ValueKey('entry-linguistic-switch'))
                  .hitTestable(),
            )
            .value,
        isTrue,
      );
      expect(
        find.text('Show each dictionary field separately.'),
        findsOneWidget,
      );
      await tester.pageBack();
      await tester.pumpAndSettle();
      await tester.tap(find.byTooltip('Dictionary options'));
      await tester.pumpAndSettle();
      expect(
        tester
            .widget<CheckedPopupMenuItem<String>>(
              find.byType(CheckedPopupMenuItem<String>),
            )
            .checked,
        isTrue,
      );
    },
  );

  testWidgets('reader continues past the first 100 browse entries', (
    tester,
  ) async {
    final json = jsonDecode(
      File('test/fixtures/dictionary.json').readAsStringSync(),
    ) as Map<String, dynamic>;
    json['entries'] = List.generate(
      105,
      (i) => {
        'id': 'main:$i',
        'headword': 'word${i.toString().padLeft(3, '0')}',
        'source': 'main',
        'language': 'Matigsalug',
        'summary': '',
        'fields': <dynamic>[],
      },
    );
    json['indexes'] = {'english': <dynamic>[], 'matigsalug': <dynamic>[]};
    await openApp(tester, dictionary: DictionaryData.fromJson(json));
    await tester.tap(find.byType(ListTile).first);
    await tester.pumpAndSettle();
    final pages = tester.widget<PageView>(
      find.byKey(const ValueKey('entry-pages')),
    );
    pages.controller!.jumpToPage(99);
    await tester.pumpAndSettle();
    expect(find.text('100 of 105'), findsOneWidget);
    await tester.tap(find.byTooltip('Next entry'));
    await tester.pumpAndSettle();
    expect(find.text('101 of 105'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('About shows real counts, version and a working MALACAI link', (
    tester,
  ) async {
    final real = parseDictionary(
      File('assets/dictionary.json').readAsStringSync(),
    );
    Uri? opened;
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: Builder(
            builder: (context) => TextButton(
              onPressed: () => showDictionaryAbout(
                context,
                real,
                websiteOpener: (uri) async {
                  opened = uri;
                  return true;
                },
              ),
              child: const Text('About'),
            ),
          ),
        ),
      ),
    );
    await tester.tap(find.text('About'));
    await tester.pumpAndSettle();
    expect(find.text('0.5'), findsOneWidget);
    expect(find.text('10,225 entries'), findsOneWidget);
    expect(find.text('Main dictionary: 7,197 entries'), findsOneWidget);
    expect(find.text('Student dictionary: 3,028 entries'), findsOneWidget);
    await tester.ensureVisible(find.text('MALACAI'));
    await tester.tap(find.text('MALACAI'));
    await tester.pumpAndSettle();
    expect(opened, Uri.parse('https://MALACAI.org'));
  });

  testWidgets('failed website opening leaves the URL available to copy', (
    tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: WebsiteLink(
            label: 'MALACAI',
            uri: Uri.parse('https://MALACAI.org'),
            opener: (_) async => false,
          ),
        ),
      ),
    );
    await tester.tap(find.text('MALACAI'));
    await tester.pumpAndSettle();
    expect(find.text('Could not open the website'), findsOneWidget);
    expect(find.byType(SelectableText), findsOneWidget);
  });

  test(
    'source and English colours retain readable contrast in both themes',
    () {
      for (final dark in [false, true]) {
        final colors = DictionaryColors(dark);
        for (final source in ['main', 'student']) {
          for (final selected in [false, true]) {
            final bg = colors
                .sourceBackground(source, selected: selected)
                .computeLuminance();
            for (final foreground in [
              colors.sourceText(source),
              colors.english,
            ]) {
              final fg = foreground.computeLuminance();
              final ratio =
                  (math.max(fg, bg) + 0.05) / (math.min(fg, bg) + 0.05);
              expect(
                ratio,
                greaterThanOrEqualTo(4.5),
                reason: '$dark $source $selected',
              );
            }
          }
        }
      }
    },
  );

  testWidgets(
    'source colours and purple English headwords adapt to dark mode',
    (tester) async {
      await openApp(tester);
      final tile = find.widgetWithText(ListTile, 'abandon');
      final initialColor = tester
          .widget<Text>(find.text('abandon'))
          .style!
          .color;
      final initialBackground = tester
          .widget<Material>(
            find.ancestor(of: tile, matching: find.byType(Material)).first,
          )
          .color;
      await tester.tap(find.byTooltip('Switch light or dark theme'));
      await tester.pumpAndSettle();
      final context = tester.element(tile);
      final palette = DictionaryColors.of(context);
      expect(Theme.of(context).brightness, Brightness.dark);
      expect(
        tester.widget<Text>(find.text('abandon')).style!.color,
        palette.english,
      );
      expect(palette.english, isNot(initialColor));
      expect(
        tester
            .widget<Material>(
              find.ancestor(of: tile, matching: find.byType(Material)).first,
            )
            .color,
        palette.sourceBackground('student'),
      );
      expect(palette.sourceBackground('student'), isNot(initialBackground));
    },
  );

  testWidgets('bundled photos enlarge and allow swiping to the next entry', (
    tester,
  ) async {
    final real = parseDictionary(
      File('assets/dictionary.json').readAsStringSync(),
    );
    final entry = real.entries.firstWhere((e) => e.headword == 'baley₁');
    expect(entry.photos, isNotEmpty);
    await tester.pumpWidget(
      MaterialApp(
        home: EntryReader(
          entries: [entry, data.entries.first],
          initialIndex: 0,
          linguistic: false,
          onLinguisticChanged: (_) {},
        ),
      ),
    );
    await tester.pumpAndSettle();
    expect(find.byType(EntryPhotos), findsNWidgets(2));
    await tester.ensureVisible(
      find.byKey(const ValueKey('enlarge-photo')).first,
    );
    await tester.tap(find.byKey(const ValueKey('enlarge-photo')).first);
    await tester.pumpAndSettle();
    expect(find.byType(InteractiveViewer), findsOneWidget);
    await tester.pageBack();
    await tester.pumpAndSettle();
    expect(find.byType(EntryPhotos), findsNWidgets(2));
    await tester.drag(
      find.byKey(const ValueKey('enlarge-photo')).first,
      const Offset(-640, 0),
    );
    await tester.pumpAndSettle();
    expect(find.text('2 of 2'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}
