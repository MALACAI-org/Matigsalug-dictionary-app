import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'dictionary.dart';
import 'about_dictionary.dart';
import 'dictionary_style.dart';
import 'entry_reader.dart';

void main() {
  LicenseRegistry.addLicense(() async* {
    yield LicenseEntryWithLineBreaks([
      'Noto Sans',
    ], await rootBundle.loadString('assets/fonts/OFL.txt'));
  });
  runApp(const DictionaryApp());
}

Future<DictionaryData> loadDictionary() async {
  final text = await rootBundle.loadString('assets/dictionary.json');
  return compute(parseDictionary, text);
}

class DictionaryApp extends StatefulWidget {
  const DictionaryApp({
    super.key,
    this.loader = loadDictionary,
    this.websiteOpener = openWebsite,
  });
  final Future<DictionaryData> Function() loader;
  final WebsiteOpener websiteOpener;
  @override
  State<DictionaryApp> createState() => _DictionaryAppState();
}

class _DictionaryAppState extends State<DictionaryApp> {
  ThemeMode _themeMode = ThemeMode.system;
  late Future<DictionaryData> _data = widget.loader();

  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'Matigsalug Dictionary',
    debugShowCheckedModeBanner: false,
    themeMode: _themeMode,
    theme: ThemeData(
      fontFamily: 'NotoSans',
      colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xff236858)),
      useMaterial3: true,
    ),
    darkTheme: ThemeData(
      fontFamily: 'NotoSans',
      colorScheme: ColorScheme.fromSeed(
        seedColor: const Color(0xff236858),
        brightness: Brightness.dark,
      ),
      useMaterial3: true,
    ),
    home: FutureBuilder<DictionaryData>(
      future: _data,
      builder: (context, snapshot) {
        if (snapshot.hasData) {
          return DictionaryHome(
            data: snapshot.data!,
            websiteOpener: widget.websiteOpener,
            onThemeChanged: () => setState(() {
              _themeMode = Theme.of(context).brightness == Brightness.dark
                  ? ThemeMode.light
                  : ThemeMode.dark;
            }),
          );
        }
        return Scaffold(
          appBar: AppBar(title: const Text('Matigsalug Dictionary')),
          body: Center(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: snapshot.hasError
                  ? Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(Icons.error_outline, size: 40),
                        const SizedBox(height: 16),
                        const Text(
                          'The offline dictionary could not be opened.',
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 12),
                        FilledButton(
                          onPressed: () {
                            final next = widget.loader();
                            setState(() {
                              _data = next;
                            });
                          },
                          child: const Text('Try again'),
                        ),
                      ],
                    )
                  : const Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        CircularProgressIndicator(),
                        SizedBox(height: 20),
                        Text('Opening your offline dictionary…'),
                      ],
                    ),
            ),
          ),
        );
      },
    ),
  );
}

class DictionaryHome extends StatefulWidget {
  const DictionaryHome({
    super.key,
    required this.data,
    required this.onThemeChanged,
    required this.websiteOpener,
  });
  final DictionaryData data;
  final VoidCallback onThemeChanged;
  final WebsiteOpener websiteOpener;
  @override
  State<DictionaryHome> createState() => _DictionaryHomeState();
}

class _DictionaryHomeState extends State<DictionaryHome> {
  final _query = TextEditingController();
  final _focus = FocusNode();
  Timer? _debounce;
  SearchLanguage _language = SearchLanguage.both;
  final Set<String> _sources = {'main', 'student'};
  DictionaryEntry? _selected;
  late SearchResults _results = widget.data.search('');
  int _limit = 100;
  bool _linguistic = false;

  @override
  void dispose() {
    _debounce?.cancel();
    _query.dispose();
    _focus.dispose();
    super.dispose();
  }

  void _search({bool resetLimit = true}) {
    _debounce?.cancel();
    setState(() {
      if (resetLimit) _limit = 100;
      _results = widget.data.search(
        _query.text,
        language: _language,
        sources: _sources,
        limit: _limit,
      );
      if (!_results.entries.any((entry) => entry.id == _selected?.id)) {
        _selected = null;
      }
    });
  }

  void _about() => showDictionaryAbout(
    context,
    widget.data,
    websiteOpener: widget.websiteOpener,
  );

  @override
  Widget build(BuildContext context) => CallbackShortcuts(
    bindings: {
      const SingleActivator(LogicalKeyboardKey.keyF, control: true):
          _focus.requestFocus,
    },
    child: Scaffold(
      appBar: AppBar(
        title: const Text('Matigsalug Dictionary'),
        actions: [
          IconButton(
            onPressed: widget.onThemeChanged,
            tooltip: 'Switch light or dark theme',
            icon: const Icon(Icons.brightness_6_outlined),
          ),
          PopupMenuButton<String>(
            tooltip: 'Dictionary options',
            onSelected: (value) {
              if (value == 'about') _about();
              if (value == 'detail') setState(() => _linguistic = !_linguistic);
            },
            itemBuilder: (_) => [
              CheckedPopupMenuItem(
                value: 'detail',
                checked: _linguistic,
                child: const Text('Linguistic details'),
              ),
              const PopupMenuItem(
                value: 'about',
                child: Text('About & attribution'),
              ),
            ],
          ),
        ],
      ),
      body: SafeArea(
        top: false,
        child: LayoutBuilder(
          builder: (context, constraints) {
            final wide = constraints.maxWidth >= 900;
            final searchPanel = Column(
              children: [
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
                  child: TextField(
                    controller: _query,
                    focusNode: _focus,
                    textInputAction: TextInputAction.search,
                    decoration: InputDecoration(
                      labelText: 'Find a word',
                      hintText: 'Matigsalug or English',
                      prefixIcon: const Icon(Icons.search),
                      border: const OutlineInputBorder(),
                      suffixIcon: IconButton(
                        tooltip: 'Clear search',
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _query.clear();
                          _search();
                          _focus.requestFocus();
                        },
                      ),
                    ),
                    onChanged: (_) {
                      _debounce?.cancel();
                      _debounce = Timer(
                        const Duration(milliseconds: 180),
                        _search,
                      );
                    },
                    onSubmitted: (_) => _search(),
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 10,
                  ),
                  child: Align(
                    alignment: Alignment.centerLeft,
                    child: Wrap(
                      spacing: 8,
                      runSpacing: 4,
                      children: [
                        for (final language in SearchLanguage.values)
                          ChoiceChip(
                            label: Text(switch (language) {
                              SearchLanguage.both => 'Both languages',
                              SearchLanguage.matigsalug => 'Matigsalug',
                              SearchLanguage.english => 'English',
                            }),
                            selected: _language == language,
                            labelStyle: language == SearchLanguage.english
                                ? TextStyle(
                                    color: DictionaryColors.of(context).english,
                                  )
                                : null,
                            onSelected: (_) {
                              _language = language;
                              _search();
                            },
                          ),
                      ],
                    ),
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: Align(
                    alignment: Alignment.centerLeft,
                    child: Wrap(
                      spacing: 8,
                      runSpacing: 4,
                      children: [
                        for (final source in ['main', 'student'])
                          FilterChip(
                            backgroundColor: DictionaryColors.of(context)
                                .sourceBackground(source),
                            selectedColor: DictionaryColors.of(context)
                                .sourceBackground(source, selected: true),
                            checkmarkColor: DictionaryColors.of(context)
                                .sourceText(source),
                            labelStyle: TextStyle(
                              color: DictionaryColors.of(context)
                                  .sourceText(source),
                            ),
                            label: Text(
                              source == 'main'
                                  ? 'Main dictionary'
                                  : 'Student dictionary',
                            ),
                            selected: _sources.contains(source),
                            onSelected: (enabled) {
                              enabled
                                  ? _sources.add(source)
                                  : _sources.remove(source);
                              _search();
                            },
                          ),
                      ],
                    ),
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 10, 16, 8),
                  child: Align(
                    alignment: Alignment.centerLeft,
                    child: Text(
                      '${_query.text.trim().isEmpty ? 'Browse' : 'Results'} · ${formatCount(_results.total)} ${_results.total == 1 ? 'entry' : 'entries'}',
                      style: Theme.of(context).textTheme.labelLarge,
                    ),
                  ),
                ),
                const Divider(height: 1),
                Expanded(
                  child: _results.entries.isEmpty
                      ? Center(
                          child: Padding(
                            padding: const EdgeInsets.all(24),
                            child: Text(
                              _sources.isEmpty
                                  ? 'Choose a dictionary above to search.'
                                  : 'No matching words.\nTry the beginning of a word, or search both languages.',
                              textAlign: TextAlign.center,
                            ),
                          ),
                        )
                      : ListView.separated(
                          key: const ValueKey('results'),
                          itemCount:
                              _results.entries.length +
                              (_results.total > _results.entries.length
                                  ? 1
                                  : 0),
                          separatorBuilder: (_, index) =>
                              const Divider(height: 1),
                          itemBuilder: (context, index) {
                            if (index == _results.entries.length) {
                              return Padding(
                                padding: const EdgeInsets.all(16),
                                child: OutlinedButton(
                                  onPressed: () {
                                    _limit += 100;
                                    _search(resetLimit: false);
                                  },
                                  child: const Text('Show more words'),
                                ),
                              );
                            }
                            final entry = _results.entries[index];
                            final colors = DictionaryColors.of(context);
                            return Material(
                              color: colors.sourceBackground(
                                entry.source,
                                selected: _selected?.id == entry.id,
                              ),
                              child: ListTile(
                                key: ValueKey(entry.id),
                                selected: _selected?.id == entry.id,
                                contentPadding: const EdgeInsets.symmetric(
                                  horizontal: 20,
                                  vertical: 6,
                                ),
                                title: Text(
                                  entry.headword,
                                  style: TextStyle(
                                    fontWeight: FontWeight.w600,
                                    color: colors.languageText(entry.language),
                                  ),
                                ),
                                subtitle: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    if (entry.summary.isNotEmpty)
                                      Text(
                                        entry.summary,
                                        maxLines: 2,
                                        overflow: TextOverflow.ellipsis,
                                        style: TextStyle(
                                          color: entry.source == 'main'
                                              ? colors.english
                                              : null,
                                        ),
                                      ),
                                    const SizedBox(height: 4),
                                    Wrap(
                                      spacing: 6,
                                      crossAxisAlignment:
                                          WrapCrossAlignment.center,
                                      children: [
                                        Text(
                                          entry.language,
                                          style: Theme.of(context)
                                              .textTheme
                                              .labelSmall
                                              ?.copyWith(
                                                color: colors.languageText(
                                                  entry.language,
                                                ),
                                              ),
                                        ),
                                        DictionarySourceLabel(
                                          source: entry.source,
                                        ),
                                      ],
                                    ),
                                  ],
                                ),
                                trailing: const Icon(Icons.chevron_right),
                                onTap: () {
                                  _focus.unfocus();
                                  if (wide) {
                                    setState(() => _selected = entry);
                                  } else {
                                    final entries = widget.data
                                        .search(
                                          _query.text,
                                          language: _language,
                                          sources: _sources,
                                          limit: widget.data.entries.length,
                                        )
                                        .entries;
                                    Navigator.of(context).push(
                                      MaterialPageRoute<void>(
                                        builder: (_) => EntryReader(
                                          data: widget.data,
                                          entries: entries,
                                          initialIndex: entries.indexWhere(
                                            (e) => e.id == entry.id,
                                          ),
                                          linguistic: _linguistic,
                                          onLinguisticChanged: (value) =>
                                              setState(
                                                () => _linguistic = value,
                                              ),
                                        ),
                                      ),
                                    );
                                  }
                                },
                              ),
                            );
                          },
                        ),
                ),
              ],
            );
            if (!wide) return searchPanel;
            return Row(
              children: [
                SizedBox(width: 390, child: searchPanel),
                const VerticalDivider(width: 1),
                Expanded(
                  child: _selected == null
                      ? const Center(
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(Icons.menu_book_outlined, size: 56),
                              SizedBox(height: 16),
                              Text('Choose a word to explore'),
                            ],
                          ),
                        )
                      : EntryView(
                          key: ValueKey(_selected!.id),
                          entry: _selected!,
                          data: widget.data,
                          linguistic: _linguistic,
                          onLinguisticChanged: (value) =>
                              setState(() => _linguistic = value),
                        ),
                ),
              ],
            );
          },
        ),
      ),
    ),
  );
}
