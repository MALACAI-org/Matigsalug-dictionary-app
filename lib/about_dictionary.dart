import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:url_launcher/url_launcher.dart';

import 'dictionary.dart';
import 'dictionary_style.dart';

const appDisplayVersion = '0.5';
typedef WebsiteOpener = Future<bool> Function(Uri);

Future<bool> openWebsite(Uri uri) =>
    launchUrl(uri, mode: LaunchMode.externalApplication);

void showDictionaryAbout(
  BuildContext context,
  DictionaryData data, {
  WebsiteOpener websiteOpener = openWebsite,
}) {
  final colors = DictionaryColors.of(context);
  showAboutDialog(
    context: context,
    applicationName: 'Matigsalug Dictionary',
    applicationVersion: appDisplayVersion,
    applicationIcon: const Icon(Icons.menu_book, size: 40),
    children: [
      const Text(
        'An offline companion for exploring Matigsalug and English.\n',
      ),
      Text(
        '${formatCount(data.entries.length)} entries',
        style: Theme.of(context).textTheme.titleMedium,
      ),
      for (final source in ['main', 'student'])
        Padding(
          padding: const EdgeInsets.only(top: 8),
          child: Text(
            '${source == 'main' ? 'Main dictionary' : 'Student dictionary'}: '
            '${formatCount(data.entries.where((e) => e.source == source).length)} entries',
            style: TextStyle(color: colors.sourceText(source)),
          ),
        ),
      const SizedBox(height: 16),
      Text(
        (data.attribution['contributors'] as String).replaceAll(
          ' / MALACAI',
          '',
        ),
      ),
      Align(
        alignment: Alignment.centerLeft,
        child: WebsiteLink(
          label: 'MALACAI',
          uri: Uri.parse('https://MALACAI.org'),
          opener: websiteOpener,
        ),
      ),
      Text('Dictionary content: ${data.attribution['license']}'),
      SelectableText(data.attribution['licenseUrl'] as String),
      const SizedBox(height: 8),
      SelectableText(data.attribution['sourceUrl'] as String),
      const SizedBox(height: 8),
      Text(data.attribution['changes'] as String),
    ],
  );
}

class WebsiteLink extends StatelessWidget {
  const WebsiteLink({
    super.key,
    required this.label,
    required this.uri,
    required this.opener,
  });
  final String label;
  final Uri uri;
  final WebsiteOpener opener;

  Future<void> _open(BuildContext context) async {
    try {
      if (await opener(uri)) return;
    } on PlatformException {
      // The URL remains available to copy if the device has no browser.
    }
    if (!context.mounted) return;
    showDialog<void>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Could not open the website'),
        content: SelectableText(
          'You can open this address in your browser:\n$uri',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) => Semantics(
    link: true,
    child: TextButton.icon(
      onPressed: () => _open(context),
      icon: const Icon(Icons.open_in_new, size: 18),
      label: Text(
        label,
        style: const TextStyle(decoration: TextDecoration.underline),
      ),
    ),
  );
}
