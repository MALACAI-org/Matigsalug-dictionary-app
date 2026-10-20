// Run explicitly with: flutter test tool/capture_preview.dart
// Writes rendered phone/desktop previews under build/previews/.
import 'dart:io';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:matigsalug_dictionary/dictionary.dart';
import 'package:matigsalug_dictionary/main.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  final data = parseDictionary(
    File('assets/dictionary.json').readAsStringSync(),
  );
  setUpAll(() async {
    final textFont = FontLoader('NotoSans');
    for (final weight in ['Regular', 'Bold', 'Italic']) {
      textFont.addFont(rootBundle.load('assets/fonts/NotoSans-$weight.ttf'));
    }
    await textFont.load();
    await (FontLoader(
      'MaterialIcons',
    )..addFont(rootBundle.load('fonts/MaterialIcons-Regular.otf'))).load();
  });

  for (final size in [const Size(390, 844), const Size(1200, 1000)]) {
    for (final dark in [false, true]) {
      testWidgets('render ${size.width.toInt()}px layout dark=$dark', (
        tester,
      ) async {
        tester.view.physicalSize = size;
        tester.view.devicePixelRatio = 1;
        addTearDown(tester.view.resetPhysicalSize);
        addTearDown(tester.view.resetDevicePixelRatio);
        final boundary = GlobalKey();
        await tester.pumpWidget(
          RepaintBoundary(
            key: boundary,
            child: DictionaryApp(loader: () async => data),
          ),
        );
        await tester.pumpAndSettle();
        if (dark) {
          await tester.tap(find.byTooltip('Switch light or dark theme'));
          await tester.pumpAndSettle();
        }
        await tester.enterText(find.byType(TextField), 'baley');
        await tester.pump(const Duration(milliseconds: 250));
        await tester.pumpAndSettle();
        Future<void> capture(String name) async {
          await tester.runAsync(() async {
            final render =
                boundary.currentContext!.findRenderObject()!
                    as RenderRepaintBoundary;
            final image = await render.toImage();
            final png = await image.toByteData(format: ui.ImageByteFormat.png);
            await Directory('build/previews').create(recursive: true);
            await File('build/previews/$name${dark ? '-dark' : ''}.png')
                .writeAsBytes(png!.buffer.asUint8List());
            image.dispose();
          });
        }

        if (size.width < 900) await capture('phone-search');
        final entry = data.entries.firstWhere((e) => e.headword == 'baley₁');
        for (final photo in entry.photos) {
          await tester.runAsync(
            () => precacheImage(
              AssetImage(photo.asset),
              tester.element(find.byType(TextField)),
            ),
          );
        }
        await tester.tap(find.widgetWithText(ListTile, 'baley₁'));
        await tester.pumpAndSettle();
        await capture(size.width < 900 ? 'phone-entry' : 'desktop');
        if (size.width < 900) {
          await Scrollable.ensureVisible(
            tester.element(find.byKey(ValueKey('sense-${entry.id}-1'))),
            alignment: 0,
          );
          await tester.pumpAndSettle();
          await capture('phone-verb');
        }
        expect(tester.takeException(), isNull);
      });
    }
  }
}
