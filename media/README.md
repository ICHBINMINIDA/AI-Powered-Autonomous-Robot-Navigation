# Demo Media Guide

This directory is reserved for real project media. Do not add stock footage or simulated screenshots that could be confused with the physical robot run.

## Recommended files

```text
media/
├── demo.gif
├── demo-video-link.txt
└── screenshots/
    ├── 01-wake-word.png
    ├── 02-command-recognized.png
    ├── 03-search-mode.png
    ├── 04-target-segmented.png
    ├── 05-alignment.png
    ├── 06-approach.png
    └── 07-stop-at-target.png
```

## Suggested 20–35 second GIF sequence

1. Show the robot and the target object.
2. Display or subtitle the wake phrase.
3. Display the command: `Go to the red ball`.
4. Show the search rotation briefly.
5. Show the SAM mask and centroid.
6. Show alignment and approach.
7. End with the robot stopped near the target.

Keep the GIF below GitHub's practical file-size limits. A width around 720–900 px and 10–15 fps is usually sufficient for a README preview.

## Full video

The full video should include:

- one continuous run without hidden cuts;
- terminal or overlay evidence of the extracted target;
- live mask visualization;
- robot search, alignment, approach, and stop;
- a short title card listing ROS 2, VOSK, Ollama, SAM, and OpenCV.

Host the full video externally and place the link in `demo-video-link.txt` and the README.

## Privacy and cleanup

Before publishing:

- blur faces, badges, screens, and private university information;
- remove server usernames, hostnames, IP addresses, and tokens;
- mute unrelated conversations;
- avoid showing credentials or SSH commands with private details;
- verify that the video accurately reflects the repository's capabilities.
