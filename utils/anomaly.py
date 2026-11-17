
import statistics


def detect_anomaly(current_usage, previous_values):

    # Need enough records for a meaningful comparison
    if len(previous_values) < 5:
        return {
            "status": "Insufficient History",
            "message": "Save at least 5 prediction records to detect unusual usage."
        }

    average = statistics.mean(previous_values)
    deviation = statistics.pstdev(previous_values)

    threshold = average + (2 * deviation)

    if current_usage > threshold:
        return {
            "status": "Unusual Consumption",
            "message": "Warning! Your electricity consumption is higher than usual."
        }

    return {
        "status": "Normal Consumption",
        "message": "Your electricity consumption is within the usual range."
    }
