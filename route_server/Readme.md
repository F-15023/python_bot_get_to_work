java -jar server_route_finder.jar -Xmx100mb

Examples of requests:

localhost:12777/type=route&point=52,54&point=lat,lon

{
    "type": "route",
	"points": [
		{
			"lat":55.763716775694576,
			"lon":52.41975904638071
		},
		{
			"lat":55.72909110871012,
			"lon":52.3920150354364
		},
		{
			"lat":55.702509332832136,
			"lon":52.32918626898636
		}
	]
}