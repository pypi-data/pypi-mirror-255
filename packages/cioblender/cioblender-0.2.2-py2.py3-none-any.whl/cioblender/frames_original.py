
import re

from cioseq.sequence import Sequence
import math

AUTO_RX = re.compile(r"^auto[, :]+(\d+)$")
FML_RX = re.compile(r"^fml[, :]+(\d+)$")

MAX_TASKS = 1000


def main_frame_sequence(chunk_size, frame_range):
    """
    Generate a Sequence containing the current chosen frames.

    This function generates a sequence of frames based on the provided frame specification and chunk size.

    :param kwargs: A dictionary of keyword arguments that may include 'frame_range' and 'chunk_size'.
    :return: A Sequence containing the chosen frames.
    """
    if not frame_range:
        return Sequence.create(1, 1)
    else:
        return Sequence.create(frame_range, chunk_size=chunk_size, chunk_strategy="progressions")


def scout_frame_sequence(main_sequence, **kwargs):
    """
    Generate a Sequence containing scout frames.

    This function generates a sequence of scout frames, which can be generated from a specified pattern
    or by subsampling the main frame sequence.

    :param main_sequence: The main frame sequence.
    :param kwargs: A dictionary of keyword arguments that may include 'scout_frames' and 'use_scout_frames'.
    :return: A Sequence containing the scout frames or None.
    """
    if not kwargs.get("use_scout_frames"):
        return

    scout_spec = kwargs.get("scout_frames")

    match = AUTO_RX.match(scout_spec)
    if match:
        samples = int(match.group(1))
        return main_sequence.subsample(samples)
    else:
        match = FML_RX.match(scout_spec)
        if match:
            samples = int(match.group(1))
            return main_sequence.calc_fml(samples)

    try:
        return Sequence.create(scout_spec).intersection(main_sequence)

    except:
        pass


def resolve_payload(**kwargs):
    """
    Resolve the payload for scout frames.

    This function calculates and returns the scout frames if the 'use_scout_frames' option is enabled.

    :param kwargs: A dictionary of keyword arguments that may include 'use_scout_frames'.
    :return: A dictionary containing the scout frames or an empty dictionary.
    """
    use_scout_frames = kwargs.get("use_scout_frames")
    if not use_scout_frames:
        return {}

    frame_info_dict = set_frame_info_panel(**kwargs)
    chunk_size = frame_info_dict.get("resolved_chunk_size")
    frame_range = kwargs.get("frame_range")
    main_seq = main_frame_sequence(chunk_size, frame_range)
    scout_sequence = scout_frame_sequence(main_seq, **kwargs)
    if scout_sequence:
        return {"scout_frames": ",".join([str(f) for f in scout_sequence])}
    return {}

def set_frame_info_panel(**kwargs):
    """
    Update fields in the Frames Info panel that are driven by frames related settings.
    """
    frame_info_dict = {}
    print("In set_frame_info_panel")
    print("kwargs is: ", kwargs)

    chunk_size = kwargs.get("chunk_size")
    frame_range = kwargs.get("frame_range")
    print("chunk_size", chunk_size)
    print("frame_range", frame_range)
    main_seq = main_frame_sequence(chunk_size, frame_range)

    task_count = main_seq.chunk_count()
    frame_count = main_seq.frame_count()

    resolved_chunk_size = cap_chunk_count(task_count, frame_count, chunk_size)
    if resolved_chunk_size > chunk_size:
        frame_info_dict["resolved_chunk_size"] = resolved_chunk_size
        main_seq = main_frame_sequence(resolved_chunk_size, frame_range)
        task_count = main_seq.chunk_count()
        frame_count = main_seq.frame_count()

    scout_seq = scout_frame_sequence(main_seq, **kwargs)

    frame_info_dict["frame_count"] = frame_count
    frame_info_dict["task_count"] = task_count
    frame_info_dict["scout_frame_spec"] = "No scout frames. All frames will be started."

    if scout_seq:
        scout_chunks = main_seq.intersecting_chunks(scout_seq)
        # if there are no intersecting chunks, there are no scout frames, which means all frames will start.
        if scout_chunks:
            scout_tasks_sequence = Sequence.create(",".join(str(chunk) for chunk in scout_chunks))
            frame_info_dict["scout_frame_count"] = len(scout_tasks_sequence)
            frame_info_dict["scout_task_count"] = len(scout_chunks)
            frame_info_dict["scout_frame_spec"] = str(scout_seq)

    print("frame_info_dict is: ", frame_info_dict)
    return frame_info_dict


def cap_chunk_count(task_count, frame_count, chunk_size):
    """Cap the number of chunks to a max value.

    This is useful for limiting the number of chunks to a reasonable
    number, e.g. for a render farm.
    """
    if task_count > MAX_TASKS:
        return math.ceil(frame_count / MAX_TASKS)

    return chunk_size

def _reconcile_chunk_size(node, **widgets):
    """
    Count the tasks, and if there are too many, increase the chunk size.
    """

    chunk_size = node.attr("chunkSize").get()
    current_frames = node.attr("frameCount").get()
    current_tasks = node.attr("taskCount").get()
    if current_tasks > MAX_TASKS:
        chunk_size = math.ceil(current_frames / MAX_TASKS)
        try:
            node.attr("chunkSize").set(chunk_size)
            pm.intFieldGrp(widgets["chunkSizeField"], edit=True, value1=chunk_size)
            pm.displayWarning(
                "{}: Chunk size was adjusted to {} to keep the number of tasks below {}.".format(
                    node.name(),
                    chunk_size,
                    MAX_TASKS
                )
            )
        except RuntimeError:
            pass

