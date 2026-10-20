import 'package:flutter/material.dart';

String formatCount(int count) => count.toString().replaceAllMapped(
  RegExp(r'(\d)(?=(\d{3})+$)'),
  (match) => '${match[1]},',
);

/// Source colours stay distinct from the purple used for English text.
class DictionaryColors {
  const DictionaryColors(this.dark);
  final bool dark;

  static DictionaryColors of(BuildContext context) =>
      DictionaryColors(Theme.of(context).brightness == Brightness.dark);

  Color sourceText(String source) => source == 'student'
      ? (dark ? const Color(0xfff2d97c) : const Color(0xff6b5100))
      : (dark ? const Color(0xffaed9b5) : const Color(0xff235b35));

  Color sourceBackground(String source, {bool selected = false}) {
    if (source == 'student') {
      return dark
          ? (selected ? const Color(0xff594a1d) : const Color(0xff403817))
          : (selected ? const Color(0xfff4e2a4) : const Color(0xfffff4cc));
    }
    return dark
        ? (selected ? const Color(0xff2a4931) : const Color(0xff193522))
        : (selected ? const Color(0xffd5e8d6) : const Color(0xffeaf4ea));
  }

  Color get english => dark ? const Color(0xffd5b7f4) : const Color(0xff673f91);
  Color languageText(String language) =>
      language == 'English' ? english : sourceText('main');
}

class DictionarySourceLabel extends StatelessWidget {
  const DictionarySourceLabel({super.key, required this.source});
  final String source;

  @override
  Widget build(BuildContext context) {
    final colors = DictionaryColors.of(context);
    return DecoratedBox(
      decoration: BoxDecoration(
        color: colors.sourceBackground(source),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        child: Text(
          source == 'main' ? 'Main dictionary' : 'Student dictionary',
          style: Theme.of(context).textTheme.labelMedium
              ?.copyWith(color: colors.sourceText(source)),
        ),
      ),
    );
  }
}
