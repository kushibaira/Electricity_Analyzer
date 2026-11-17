
def get_recommendations(consumption):

    recommendations = []

    if consumption > 18:
        recommendations.append(
            "Your electricity usage is high. Switch off unused appliances."
        )
        recommendations.append(
            "Reduce unnecessary air conditioner usage."
        )

    elif consumption > 13:
        recommendations.append(
            "Your electricity usage is moderate. Use energy-efficient appliances."
        )
        recommendations.append(
            "Avoid keeping devices on standby."
        )

    else:
        recommendations.append(
            "Your electricity usage is low. Keep maintaining these habits."
        )
        recommendations.append(
            "Continue switching off unused lights and fans."
        )

    return recommendations
