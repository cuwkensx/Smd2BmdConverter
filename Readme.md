# Convert .smd to .bmd

Support SMD models and animations. This repo currently only converts smd to bmd, it cannot do the reverse. (it's not much work to implement though, you can help me with that :> )

## Usage

```shell
python smd2bmd.py --file /path/to/your/smd
```

The converted bmd will be saved to the same directory of your smd file.

## Requirements

Python, any version may goes.

Nothing else.

## Why Python

No need to compile, easy to debug and modify, CLI support which is friendly to multiprocessing and batch processing.

## Future work

1. .bmd to .smd conversion.

2. Batch and multiprocess support.
