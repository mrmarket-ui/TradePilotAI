from services.recommendations.priority import sort_recommendations

recommendations = [

    {
        "priority":"Low",
        "title":"Low"
    },

    {
        "priority":"Critical",
        "title":"Critical"
    },

    {
        "priority":"High",
        "title":"High"
    },

    {
        "priority":"Medium",
        "title":"Medium"
    }

]

result = sort_recommendations(recommendations)

for recommendation in result:

    print(
        recommendation["priority"],
        recommendation["title"]
    )
