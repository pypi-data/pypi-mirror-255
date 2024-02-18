# TODO

## Create Offline Presentations

Find a reliable way to create offline presentations automatically. It is possible to do this manually by saving the page as "Web Page, Complete" via modern browsers but this downloads the external files each time and requires an internet connection each time the presentation is updated.

The ideal solution would do the following:

1. Detect all external resources, including those used in Javascript.
2. Assign consistent UUIDs to each resource.
3. Ensure all resources are cached locally.
4. Mangle the HTML to use the local files.

It would then be possible to update slides completely offline as long as the update does not introduce new external resources.
