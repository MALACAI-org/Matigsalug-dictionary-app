import 'package:flutter/material.dart';

import 'definition_text.dart';
import 'dictionary.dart';
import 'dictionary_style.dart';
import 'entry_photos.dart';
import 'entry_sections.dart';

class EntrySectionView extends StatelessWidget {
  const EntrySectionView({
    super.key,
    required this.entry,
    required this.section,
    required this.linguistic,
    required this.sectionIndex,
    this.data,
    this.onOpen,
  });
  final DictionaryEntry entry;
  final EntrySection section;
  final int sectionIndex;
  final bool linguistic;
  final DictionaryData? data;
  final OpenDictionaryWord? onOpen;

  @override
  Widget build(BuildContext context) {
    final title = [
      if (section.sense != null) section.sense!,
      if (section.subentry != null) section.subentry!,
      if (section.partOfSpeech != null) partOfSpeechLabel(section.partOfSpeech),
    ].join(' · ');
    final children = <Widget>[
      if (!linguistic && title.isNotEmpty)
        Padding(
          padding: const EdgeInsets.only(bottom: 12),
          child: Text(
            title,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              color: DictionaryColors.of(context).sourceText(entry.source),
            ),
          ),
        ),
    ];
    int? photoAfter;
    if (linguistic) {
      for (final f in section.fields) {
        children.add(
          EntryFieldView(
            field: f,
            entry: entry,
            detailed: true,
            data: data,
            onOpen: onOpen,
          ),
        );
        if (f.marker == (entry.source == 'main' ? 'gl' : 'de')) {
          photoAfter ??= children.length;
        }
      }
    } else {
      final blocks = normalBlocks(section, entry.source);
      for (final block in blocks) {
        if (block.kind == 'meaning') {
          children.add(
            Padding(
              padding: const EdgeInsets.only(bottom: 14),
              child: DefinitionText(
                runs: block.meaning,
                language: SearchLanguage.english,
                entryId: entry.id,
                data: data,
                onOpen: onOpen,
                style: Theme.of(context).textTheme.bodyLarge!.copyWith(
                  fontSize: 18,
                  height: 1.45,
                  color: DictionaryColors.of(context).english,
                ),
              ),
            ),
          );
          photoAfter ??= children.length;
        } else if (block.kind == 'example') {
          children.add(
            Container(
              margin: const EdgeInsets.only(bottom: 16),
              padding: const EdgeInsets.only(left: 12),
              decoration: BoxDecoration(
                border: Border(
                  left: BorderSide(
                    color: Theme.of(context).colorScheme.outlineVariant,
                    width: 2,
                  ),
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: block.fields
                    .map(
                      (f) => EntryFieldView(
                        field: f,
                        entry: entry,
                        detailed: false,
                        data: data,
                        onOpen: onOpen,
                      ),
                    )
                    .toList(),
              ),
            ),
          );
        } else {
          children.addAll(
            block.fields.map(
              (f) => EntryFieldView(
                field: f,
                entry: entry,
                detailed: false,
                data: data,
                onOpen: onOpen,
              ),
            ),
          );
          if (block.fields.any((f) => f.marker == 'de')) {
            photoAfter ??= children.length;
          }
        }
      }
      if (blocks.isEmpty) {
        children.add(
          const Text('More information is available in Linguistic details.'),
        );
      }
    }
    final words = Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: children,
    );
    return Padding(
      padding: const EdgeInsets.only(bottom: 24),
      child: LayoutBuilder(
        builder: (context, constraints) {
          if (section.photos.isEmpty) return words;
          final photos = EntryPhotos(
            key: ValueKey('section-photos-${entry.id}-$sectionIndex'),
            photos: section.photos,
          );
          // Keep a useful text column on narrow windows and at large text sizes.
          final beside =
              constraints.maxWidth >= 620 &&
              MediaQuery.textScalerOf(context).scale(18) <= 24;
          if (beside) {
            return Row(
              key: ValueKey('sense-row-$sectionIndex'),
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(child: words),
                const SizedBox(width: 24),
                SizedBox(width: 220, child: photos),
              ],
            );
          }
          // Portrait layouts keep each image immediately with its definition,
          // before the examples, rather than at the top of the whole entry.
          final lead = children.take(photoAfter ?? 1);
          return Column(
            key: ValueKey('sense-column-$sectionIndex'),
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              ...lead,
              photos,
              const SizedBox(height: 16),
              ...children.skip(lead.length),
            ],
          );
        },
      ),
    );
  }
}

class EntryFieldView extends StatelessWidget {
  const EntryFieldView({
    super.key,
    required this.field,
    required this.entry,
    required this.detailed,
    this.data,
    this.onOpen,
  });
  final EntryField field;
  final DictionaryEntry entry;
  final bool detailed;
  final DictionaryData? data;
  final OpenDictionaryWord? onOpen;

  @override
  Widget build(BuildContext context) {
    final marker = field.marker;
    final main = entry.source == 'main';
    final english = main
        ? {'gl', 'gli', 'tr', 'de'}.contains(marker)
        : {'xv', 'dv'}.contains(marker);
    final example = main
        ? {'ex', 'tr'}.contains(marker)
        : {'xv', 'xe'}.contains(marker);
    final implicitLabel =
        example ||
        (main ? {'df'}.contains(marker) : {'de', 'dv'}.contains(marker));
    final linkable = main
        ? {'gl', 'gli', 'df', 'rs', 'ra', 'ro', 'rm'}.contains(marker)
        : {'de', 'dv', 'df', 'mn', 'cf'}.contains(marker);
    final linkLanguage = main
        ? (english ? SearchLanguage.english : SearchLanguage.matigsalug)
        : ({'dv', 'mn', 'cf'}.contains(marker)
              ? SearchLanguage.english
              : SearchLanguage.matigsalug);
    final style = Theme.of(context).textTheme.bodyLarge!.copyWith(
      height: 1.5,
      color: english ? DictionaryColors.of(context).english : null,
      fontWeight: {'gl', 'de', 'oi', 'se'}.contains(marker)
          ? FontWeight.w600
          : FontWeight.normal,
      fontSize: !detailed && !main && marker == 'de' ? 20 : null,
      fontStyle: {'ex', 'xv'}.contains(marker) || (main && marker == 'sn')
          ? FontStyle.italic
          : FontStyle.normal,
    );
    return Padding(
      padding: EdgeInsets.only(bottom: !detailed && example ? 4 : 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (detailed || !implicitLabel) ...[
            Text(
              main && marker == 'sn' ? 'Scientific name' : field.label,
              style: Theme.of(context).textTheme.labelMedium?.copyWith(
                color: DictionaryColors.of(context).sourceText(entry.source),
              ),
            ),
            const SizedBox(height: 3),
          ],
          if (linkable)
            DefinitionText(
              runs: [MeaningRun(field.text)],
              language: linkLanguage,
              entryId: entry.id,
              style: style,
              data: data,
              onOpen: onOpen,
            )
          else
            Text(field.text, style: style),
        ],
      ),
    );
  }
}
