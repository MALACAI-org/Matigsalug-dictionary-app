import 'package:flutter/material.dart';

import 'dictionary.dart';
import 'dictionary_style.dart';

class EntryPhotos extends StatefulWidget {
  const EntryPhotos({super.key, required this.photos});
  final List<DictionaryPhoto> photos;

  @override
  State<EntryPhotos> createState() => _EntryPhotosState();
}

class _EntryPhotosState extends State<EntryPhotos> {
  int _index = 0;

  @override
  Widget build(BuildContext context) {
    final photo = widget.photos[_index];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SizedBox(height: 16),
        Semantics(
          button: true,
          label: 'Enlarge photo: ${photo.caption}',
          child: InkWell(
            key: const ValueKey('enlarge-photo'),
            onTap: () => Navigator.of(context).push(
              MaterialPageRoute<void>(
                builder: (_) => Scaffold(
                  appBar: AppBar(title: Text(photo.caption)),
                  body: SafeArea(
                    child: InteractiveViewer(
                      minScale: 1,
                      maxScale: 4,
                      child: Center(child: _photoImage(photo)),
                    ),
                  ),
                ),
              ),
            ),
            child: SizedBox(
              height: 180,
              width: double.infinity,
              child: ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: _photoImage(photo),
              ),
            ),
          ),
        ),
        Row(
          children: [
            if (widget.photos.length > 1)
              IconButton(
                tooltip: 'Previous photo',
                onPressed: _index > 0 ? () => setState(() => _index--) : null,
                icon: const Icon(Icons.chevron_left),
              ),
            Expanded(
              child: Text(
                '${photo.caption} · Photo ${formatCount(_index + 1)} of ${formatCount(widget.photos.length)}',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ),
            if (widget.photos.length > 1)
              IconButton(
                tooltip: 'Next photo',
                onPressed: _index + 1 < widget.photos.length
                    ? () => setState(() => _index++)
                    : null,
                icon: const Icon(Icons.chevron_right),
              ),
          ],
        ),
      ],
    );
  }

  Widget _photoImage(DictionaryPhoto photo) => Image.asset(
    photo.asset,
    fit: BoxFit.contain,
    semanticLabel: photo.caption,
    errorBuilder: (_, error, stackTrace) =>
        const Center(child: Text('Photo unavailable')),
  );
}
