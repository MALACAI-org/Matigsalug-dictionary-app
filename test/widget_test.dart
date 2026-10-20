import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:matigsalug_dictionary/dictionary.dart';
import 'package:matigsalug_dictionary/main.dart';
import 'package:matigsalug_dictionary/entry_reader.dart';

void main() {
  late DictionaryData data;
  setUp(
    () => data = parseDictionary(
      File('test/fixtures/dictionary.json').readAsStringSync(),
    ),
  );

  Future<void> openApp(WidgetTester tester, Size size) async {
    tester.view.physicalSize = size;
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(DictionaryApp(loader: () async => data));
    await tester.pumpAndSettle();
  }

  testWidgets('phone search opens an entry and back preserves the query', (
    tester,
  ) async {
    await openApp(tester, const Size(390, 844));
    await tester.enterText(find.byType(TextField), 'abandon');
    await tester.pump(const Duration(milliseconds: 250));
    await tester.pumpAndSettle();
    expect(find.text('Results · 1 entry'), findsOneWidget);
    await tester.tap(find.byType(ListTile).first);
    await tester.pumpAndSettle();
    expect(find.text('English explanation'), findsNothing);
    expect(find.text('Leave someone.'), findsOneWidget);
    await tester.pageBack();
    await tester.pumpAndSettle();
    expect(find.widgetWithText(TextField, 'abandon'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('desktop shows selected entry beside results', (tester) async {
    await openApp(tester, const Size(1200, 800));
    expect(find.text('Choose a word to explore'), findsOneWidget);
    await tester.tap(find.byType(ListTile).first);
    await tester.pumpAndSettle();
    expect(find.byType(TextField), findsOneWidget);
    expect(find.byType(EntryView), findsOneWidget);
    expect(find.byType(BackButton), findsNothing);
    expect(tester.takeException(), isNull);
  });

  testWidgets('small phone handles larger system text', (tester) async {
    tester.platformDispatcher.textScaleFactorTestValue = 1.8;
    addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
    await openApp(tester, const Size(320, 700));
    expect(tester.takeException(), isNull);
  });

  testWidgets('missing data shows a retry action and recovers', (tester) async {
    var attempts = 0;
    await tester.pumpWidget(
      DictionaryApp(
        loader: () async {
          if (attempts++ == 0) throw const FormatException('broken asset');
          return data;
        },
      ),
    );
    await tester.pumpAndSettle();
    expect(
      find.text('The offline dictionary could not be opened.'),
      findsOneWidget,
    );
    await tester.tap(find.text('Try again'));
    await tester.pumpAndSettle();
    expect(find.byType(TextField), findsOneWidget);
  });
}
