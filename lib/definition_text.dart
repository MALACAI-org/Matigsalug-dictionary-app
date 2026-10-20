import 'package:flutter/material.dart';

import 'dictionary.dart';
import 'entry_sections.dart';

typedef OpenDictionaryWord = void Function(
  String word,
  List<DictionaryEntry> entries,
);

/// Leave grammatical glue as plain text, so definitions remain readable.
/// Matches are whole words in the appropriate language, never prefix guesses.
class DefinitionText extends StatelessWidget {
  const DefinitionText({
    super.key,
    required this.runs,
    required this.language,
    required this.entryId,
    required this.style,
    this.data,
    this.onOpen,
  });
  final List<MeaningRun> runs;
  final SearchLanguage language;
  final String entryId;
  final TextStyle style;
  final DictionaryData? data;
  final OpenDictionaryWord? onOpen;

  static final _words = RegExp(
    r"[\p{L}\p{M}₀-₉]+(?:[-’'][\p{L}\p{M}₀-₉]+)*",
    unicode: true,
  );
  static const _englishGlue = {
    'a',
    'an',
    'the',
    'to',
    'for',
    'of',
    'in',
    'on',
    'at',
    'by',
    'with',
    'from',
    'as',
    'and',
    'or',
    'but',
    'if',
    'than',
    'that',
    'this',
    'these',
    'those',
    'it',
    'its',
    'is',
    'are',
    'was',
    'were',
    'be',
    'been',
    'being',
    'do',
    'does',
    'did',
    'have',
    'has',
    'had',
    'someone',
    'something',
    'somewhere',
    'anyone',
    'anything',
    'any',
    'some',
    'one',
    's',
    'e',
    'g',
    'i',
    'you',
    'he',
    'she',
    'we',
    'they',
    'them',
    'their',
    'his',
    'her',
    'my',
    'your',
    'our',
    'me',
    'us',
    'him',
    'who',
    'which',
    'not',
    'can',
    'could',
    'would',
    'should',
    'will',
    'shall',
    'may',
    'might',
    'must',
  };

  @override
  Widget build(BuildContext context) {
    final spans = <InlineSpan>[];
    for (var i = 0; i < runs.length; i++) {
      if (i > 0) spans.add(const TextSpan(text: ' '));
      final run = runs[i];
      final runStyle = run.emphasized
          ? style.copyWith(
              fontWeight: FontWeight.w700,
              fontSize: (style.fontSize ?? 18) + 2,
            )
          : style;
      var position = 0;
      for (final match in _words.allMatches(run.text)) {
        if (match.start > position) {
          spans.add(
            TextSpan(
              text: run.text.substring(position, match.start),
              style: runStyle,
            ),
          );
        }
        final word = match.group(0)!;
        final eligible =
            onOpen != null &&
            data != null &&
            word.length > 1 &&
            !(language == SearchLanguage.english &&
                _englishGlue.contains(word.toLowerCase()));
        final targets = eligible
            ? data!
                  .exactMatches(word, language: language)
                  .where((e) => e.id != entryId)
                  .toList()
            : <DictionaryEntry>[];
        if (targets.isEmpty) {
          spans.add(TextSpan(text: word, style: runStyle));
        } else {
          // Inline widgets keep links keyboard-focusable as well as tappable.
          spans.add(
            WidgetSpan(
              alignment: PlaceholderAlignment.baseline,
              baseline: TextBaseline.alphabetic,
              child: Tooltip(
                message: 'Look up $word',
                child: Semantics(
                  link: true,
                  child: InkWell(
                    onTap: () => onOpen!(word, targets),
                    borderRadius: BorderRadius.circular(3),
                    child: Text(
                      word,
                      style: runStyle.copyWith(
                        decoration: TextDecoration.underline,
                        decorationStyle: TextDecorationStyle.dotted,
                      ),
                    ),
                  ),
                ),
              ),
            ),
          );
        }
        position = match.end;
      }
      if (position < run.text.length) {
        spans.add(
          TextSpan(text: run.text.substring(position), style: runStyle),
        );
      }
    }
    return Text.rich(TextSpan(children: spans), style: style);
  }
}
