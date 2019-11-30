import os
import logging

from django.contrib.staticfiles.finders import get_finders
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.files.storage import FileSystemStorage

logger = logging.getLogger(__name__)


class CollectorError(Exception):
    pass


class Collector:
    """
    Copies or symlinks static files from different locations to the
    settings.STATIC_ROOT.
    """

    def __init__(
        self, symlink: bool = False, clear: bool = False,
        dry_run: bool = False, post_process: bool = True,
    ):
        self.symlink = symlink
        self.clear = clear
        self.dry_run = dry_run
        self.post_process = post_process
        self.ignore_patterns = []
        self.copied_files = []
        self.symlinked_files = []
        self.unmodified_files = []
        self.post_processed_files = []
        self.storage = staticfiles_storage

    @property
    def local(self):
        try:
            self.storage.path('')
        except NotImplementedError:
            return False
        return True

    def collect(self):
        """
        Perform the bulk of the work of collectstatic.
        Split off from handle() to facilitate testing.
        """
        if self.symlink and not self.local:
            raise CollectorError("Can't symlink to a remote destination.")

        if self.clear:
            self.clear_dir('')

        if self.symlink:
            handler = self.link_file
        else:
            handler = self.copy_file

        found_files = {}
        for finder in get_finders():
            for path, storage in finder.list(self.ignore_patterns):
                # Prefix the relative path if the source storage contains it
                if getattr(storage, 'prefix', None):
                    prefixed_path = os.path.join(storage.prefix, path)
                else:
                    prefixed_path = path

                if prefixed_path not in found_files:
                    found_files[prefixed_path] = (storage, path)
                    handler(path, prefixed_path, storage)
                else:
                    logger.warning(
                        "Found another file with the destination path '%s'. "
                        "It will be ignored since only the first encountered "
                        "file is collected. If this is not what you want, "
                        "make sure every static file has a unique path.",
                        prefixed_path,
                    )

        # Storage backends may define a post_process() method.
        if self.post_process and hasattr(self.storage, 'post_process'):
            processor = self.storage.post_process(
                found_files, dry_run=self.dry_run,
            )
            for original_path, processed_path, processed in processor:
                if isinstance(processed, Exception):
                    logger.error(
                        "Post-processing '%s' failed!" % original_path,
                    )
                    raise processed
                if processed:
                    logger.debug(
                        "Post-processed '%s' as '%s'",
                        original_path, processed_path,
                    )
                else:
                    logger.debug("Skipped post-processing '%s'", original_path)

        return {
            'modified': self.copied_files + self.symlinked_files,
            'unmodified': self.unmodified_files,
            'post_processed': self.post_processed_files,
        }

    def handle(self):
        logger.info('Collecting static files')

        if self.dry_run:
            logger.info('Dry run activated, no files will be modified')

        if self.is_local_storage() and self.storage.location:
            destination_path = self.storage.location
            logger.debug(
                "Local static files destination '%s'", destination_path,
            )
            should_warn_user = (
                self.storage.exists(destination_path) and
                any(self.storage.listdir(destination_path))
            )
        else:
            destination_path = None
            # Destination files existence not checked; play it safe and warn.
            should_warn_user = True

        if should_warn_user:
            if self.clear:
                logger.debug('Deleting all files at static files destination')
            else:
                logger.debug('Overwriting files at static files destination')

        collected = self.collect()
        modified_count = len(collected['modified'])
        unmodified_count = len(collected['unmodified'])
        post_processed_count = len(collected['post_processed'])
        template = (
            "%(modified_count)s %(identifier)s %(action)s"
            "%(destination)s%(unmodified)s%(post_processed)s."
        )
        summary = template % {
            'modified_count': modified_count,
            'identifier': 'static file' + ('' if modified_count == 1 else 's'),
            'action': 'symlinked' if self.symlink else 'copied',
            'destination': (
                " to '%s'" % destination_path
                if destination_path else ''
            ),
            'unmodified': (
                ', %s unmodified' % unmodified_count
                if collected['unmodified'] else ''
            ),
            'post_processed': (
                collected['post_processed'] and
                ', %s post-processed'
                % post_processed_count or ''
            ),
        }
        logger.info(summary)

    def is_local_storage(self):
        return isinstance(self.storage, FileSystemStorage)

    def clear_dir(self, path):
        """
        Delete the given relative path using the destination storage backend.
        """
        if not self.storage.exists(path):
            return

        dirs, files = self.storage.listdir(path)
        for f in files:
            fpath = os.path.join(path, f)
            if self.dry_run:
                logger.debug("Pretending to delete '%s'", fpath)
            else:
                logger.debug("Deleting '%s'", fpath)
                try:
                    full_path = self.storage.path(fpath)
                except NotImplementedError:
                    self.storage.delete(fpath)
                else:
                    lexists = os.path.lexists(full_path)
                    if not os.path.exists(full_path) and lexists:
                        # Delete broken symlinks
                        os.unlink(full_path)
                    else:
                        self.storage.delete(fpath)
        for d in dirs:
            self.clear_dir(os.path.join(path, d))

    def delete_file(self, path, prefixed_path, source_storage):
        """
        Check if the target file should be deleted if it already exists.
        """
        if self.storage.exists(prefixed_path):
            try:
                # When was the target file modified last time?
                target_last_modified = self.storage.get_modified_time(
                    prefixed_path,
                )
            except (OSError, NotImplementedError, AttributeError):
                # The storage doesn't support get_modified_time() or failed
                pass
            else:
                try:
                    # When was the source file modified last time?
                    source_last_modified = source_storage.get_modified_time(
                        path,
                    )
                except (OSError, NotImplementedError, AttributeError):
                    pass
                else:
                    # The full path of the target file
                    if self.local:
                        full_path = self.storage.path(prefixed_path)
                        # If it's --link mode and the path isn't a link (i.e.
                        # the previous collectstatic wasn't with --link) or if
                        # it's non-link mode and the path is a link (i.e. the
                        # previous collectstatic was with --link), the old
                        # links/files must be deleted so it's not safe to skip
                        # unmodified files.
                        can_skip_unmodified_files = not (
                            self.symlink ^ os.path.islink(full_path)
                        )
                    else:
                        # In remote storages, skipping is only based on the
                        # modified times since symlinks aren't relevant.
                        can_skip_unmodified_files = True
                    # Avoid sub-second precision (see #14665, #19540)
                    file_is_unmodified = (
                        target_last_modified.replace(microsecond=0) >=
                        source_last_modified.replace(microsecond=0)
                    )
                    if file_is_unmodified and can_skip_unmodified_files:
                        if prefixed_path not in self.unmodified_files:
                            self.unmodified_files.append(prefixed_path)
                        logger.debug("Skipping '%s' (not modified)", path)
                        return False
            # Then delete the existing file if really needed
            if self.dry_run:
                logger.info("Pretending to delete '%s'", path)
            else:
                logger.info("Deleting '%s'", path)
                self.storage.delete(prefixed_path)
        return True

    def link_file(self, path, prefixed_path, source_storage):
        """
        Attempt to link ``path``
        """
        # Skip this file if it was already copied earlier
        if prefixed_path in self.symlinked_files:
            return logger.debug("Skipping '%s' (already linked earlier)", path)
        # Delete the target file if needed or break
        if not self.delete_file(path, prefixed_path, source_storage):
            return
        # The full path of the source file
        source_path = source_storage.path(path)
        # Finally link the file
        if self.dry_run:
            logger.info("Pretending to link '%s'", source_path)
        else:
            logger.info("Linking '%s'", source_path)
            full_path = self.storage.path(prefixed_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            try:
                if os.path.lexists(full_path):
                    os.unlink(full_path)
                os.symlink(source_path, full_path)
            except AttributeError:
                import platform
                raise CollectorError(
                    "Symlinking is not supported by Python %s." %
                    platform.python_version(),
                )
            except NotImplementedError:
                import platform
                raise CollectorError(
                    "Symlinking is not supported in this "
                    "platform (%s)." % platform.platform(),
                )
            except OSError as e:
                raise CollectorError(e)
        if prefixed_path not in self.symlinked_files:
            self.symlinked_files.append(prefixed_path)

    def copy_file(self, path, prefixed_path, source_storage):
        """
        Attempt to copy ``path`` with storage
        """
        # Skip this file if it was already copied earlier
        if prefixed_path in self.copied_files:
            return logger.debug("Skipping '%s' (already copied earlier)", path)
        # Delete the target file if needed or break
        if not self.delete_file(path, prefixed_path, source_storage):
            return
        # The full path of the source file
        source_path = source_storage.path(path)
        # Finally start copying
        if self.dry_run:
            logger.info("Pretending to copy '%s'", source_path)
        else:
            logger.info("Copying '%s'", source_path)
            with source_storage.open(path) as source_file:
                self.storage.save(prefixed_path, source_file)
        self.copied_files.append(prefixed_path)
