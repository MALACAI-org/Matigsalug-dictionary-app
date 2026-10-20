import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'dictionary.dart';
import 'dictionary_style.dart';
import 'entry_photos.dart';
import 'entry_content.dart';
import 'entry_sections.dart';

/// Takes a complete snapshot of the filtered results, beyond list pagination.
class EntryReader extends StatefulWidget {
  const EntryReader({
    super.key,
    required this.entries,
    required this.initialIndex,
    required this.linguistic,
    required this.onLinguisticChanged,
    this.data,
  });
  final DictionaryData? data;
  final List<DictionaryEntry> entries;
  final int initialIndex;
  final bool linguistic;
  final ValueChanged<bool> onLinguisticChanged;

  @override
  State<EntryReader> createState() => _EntryReaderState();
}

class _EntryReaderState extends State<EntryReader> {
  late final PageController _pages = PageController(
    initialPage: widget.initialIndex,
  );
  late int _index = widget.initialIndex;
  late bool _linguistic = widget.linguistic;

  @override
  void dispose() {
    _pages.dispose();
    super.dispose();
  }

  void _step(int delta) {
    final next = _index + delta;
    if (next < 0 || next >= widget.entries.length) return;
    _pages.animateToPage(
      next,
      duration: const Duration(milliseconds: 220),
      curve: Curves.easeInOut,
    );
  }

  @override
  Widget build(BuildContext context) {
    final entry = widget.entries[_index];
    return CallbackShortcuts(
      bindings: {
        const SingleActivator(LogicalKeyboardKey.arrowLeft): () => _step(-1),
        const SingleActivator(LogicalKeyboardKey.arrowRight): () => _step(1),
      },
      child: Focus(
        autofocus: true,
        child: Scaffold(
          appBar: AppBar(
            title: Text(
              entry.headword,
              style: TextStyle(
                color: DictionaryColors.of(context)
                    .languageText(entry.language),
              ),
            ),
          ),
          body: SafeArea(
            child: Column(
              children: [
                Expanded(
                  child: PageView.builder(
                    key: const ValueKey('entry-pages'),
                    controller: _pages,
                    itemCount: widget.entries.length,
                    onPageChanged: (index) => setState(() => _index = index),
                    itemBuilder: (context, index) => EntryView(
                      key: ValueKey(widget.entries[index].id),
                      entry: widget.entries[index],
                      data: widget.data,
                      selectable: false,
                      linguistic: _linguistic,
                      onLinguisticChanged: (value) {
                        setState(() => _linguistic = value);
                        widget.onLinguisticChanged(value);
                      },
                    ),
                  ),
                ),
                const Divider(height: 1),
                Padding(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  child: Row(
                    children: [
                      IconButton(
                        tooltip: 'Previous entry',
                        onPressed: _index > 0 ? () => _step(-1) : null,
                        icon: const Icon(Icons.chevron_left),
                      ),
                      Expanded(
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(
                              '${formatCount(_index + 1)} of ${formatCount(widget.entries.length)}',
                              key: const ValueKey('entry-position'),
                            ),
                            if (widget.entries.length > 1)
                              Text(
                                'Swipe left or right to change entries',
                                textAlign: TextAlign.center,
                                style: Theme.of(context).textTheme.bodySmall,
                              ),
                          ],
                        ),
                      ),
                      IconButton(
                        tooltip: 'Next entry',
                        onPressed: _index + 1 < widget.entries.length
                            ? () => _step(1)
                            : null,
                        icon: const Icon(Icons.chevron_right),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class EntryView extends StatelessWidget {
  const EntryView({
    super.key,
    required this.entry,
    required this.linguistic,
    required this.onLinguisticChanged,
    this.selectable = true,
    this.data,
  });
  final DictionaryEntry entry;
  final bool linguistic;
  final ValueChanged<bool> onLinguisticChanged;
  final bool selectable;
  final DictionaryData? data;

  Future<void> _openWord(
    BuildContext context,
    String word,
    List<DictionaryEntry> matches,
  ) async {
    DictionaryEntry? chosen;
    if (matches.length == 1) {
      chosen = matches.single;
    } else {
      chosen = await showDialog<DictionaryEntry>(
        context: context,
        builder: (context) => AlertDialog(
          title: Text('Choose an entry for “$word”'),
          content: SizedBox(
            width: 480,
            height: 360,
            child: ListView.separated(
              itemCount: matches.length,
              separatorBuilder: (_, index) => const Divider(height: 1),
              itemBuilder: (context, index) {
                final target = matches[index];
                return ListTile(
                  key: ValueKey('link-choice-${target.id}'),
                  title: Text(target.headword),
                  subtitle: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        target.summary,
                        maxLines: 3,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 4),
                      DictionarySourceLabel(source: target.source),
                    ],
                  ),
                  onTap: () => Navigator.of(context).pop(target),
                );
              },
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Cancel'),
            ),
          ],
        ),
      );
    }
    if (chosen == null || !context.mounted) return;
    final target = chosen;
    await Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (_) => EntryReader(
          entries: [target],
          initialIndex: 0,
          data: data,
          linguistic: linguistic,
          onLinguisticChanged: onLinguisticChanged,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colors = DictionaryColors.of(context);
    final presentation = EntrySections(
      entry,
      data?.normalize ?? (text) => text.toLowerCase().trim(),
    );
    final technicalCount = entry.fields
        .where((f) => isDetailedField(entry.source, f.marker))
        .length;
    void openWord(String word, List<DictionaryEntry> matches) =>
        _openWord(context, word, matches);
    final content = SingleChildScrollView(
      key: PageStorageKey('entry-scroll-${entry.id}'),
      padding: const EdgeInsets.all(24),
      child: Align(
        alignment: Alignment.topLeft,
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1000),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                entry.language.toUpperCase(),
                style: theme.textTheme.labelLarge?.copyWith(
                  color: colors.languageText(entry.language),
                ),
              ),
              const SizedBox(height: 8),
              Text(
                entry.headword,
                style: theme.textTheme.headlineLarge?.copyWith(
                  color: colors.languageText(entry.language),
                ),
              ),
              const SizedBox(height: 8),
              DictionarySourceLabel(source: entry.source),
              const SizedBox(height: 12),
              SwitchListTile.adaptive(
                key: const ValueKey('entry-linguistic-switch'),
                contentPadding: EdgeInsets.zero,
                title: const Text('Linguistic details'),
                subtitle: Text(
                  technicalCount == 0
                      ? 'Show each dictionary field separately.'
                      : 'Show ${formatCount(technicalCount)} extra fields and the detailed layout.',
                ),
                value: linguistic,
                onChanged: onLinguisticChanged,
              ),
              const Divider(height: 24),
              for (final field in presentation.preface)
                if (linguistic || !isDetailedField(entry.source, field.marker))
                  EntryFieldView(
                    field: field,
                    entry: entry,
                    detailed: linguistic,
                    data: data,
                    onOpen: openWord,
                  ),
              for (var i = 0; i < presentation.sections.length; i++) ...[
                if (i > 0) const Divider(height: 28),
                EntrySectionView(
                  key: ValueKey('sense-${entry.id}-$i'),
                  entry: entry,
                  section: presentation.sections[i],
                  sectionIndex: i,
                  linguistic: linguistic,
                  data: data,
                  onOpen: openWord,
                ),
              ],
              if (presentation.unplacedPhotos.isNotEmpty) ...[
                Text(
                  'Other photos for this entry',
                  style: theme.textTheme.titleMedium,
                ),
                const SizedBox(height: 8),
                EntryPhotos(
                  key: ValueKey('unplaced-photos-${entry.id}'),
                  photos: presentation.unplacedPhotos,
                ),
              ],
            ],
          ),
        ),
      ),
    );
    // SelectionArea claims horizontal touch drags before the parent PageView.
    // Keep text selection in the desktop pane and swipes in the paged reader.
    return selectable ? SelectionArea(child: content) : content;
  }
}
