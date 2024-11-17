def update_progress_bar(progress_bar, current, total):
    try:
        progress = current / total
        progress_bar.set(progress)
        print(f"Progress: {progress * 100:.2f}%")
    except Exception as e:
        print(f"Failed to update progress bar: {e}")
