# pip install sellpath_test==0.0.23
from sellpath_test import ClientMgr

# it doesn't have to be a valid tenant_id in this case
client = ClientMgr("2c0e49a6-28f1-4dd2-80b8-372c03982b8d")

geo_mapping = client.get_client(app_type="geo-mapping", env_tag="production")
geo_mapping_params = {"q": "san francisco"}
geo_mapping_result = geo_mapping.get(path="/search", params=geo_mapping_params)

print(f"geo_mapping_result: {geo_mapping_result}")

latitude = geo_mapping_result["body"][0]["lat"]
longitude = geo_mapping_result["body"][0]["lon"]

print(f"lat:{latitude},lon:{longitude}")

weather = client.get_client(app_type="weather", env_tag="production")
weather_params = {
    "latitude": latitude,
    "longitude": longitude,
    "current": "temperature_2m,wind_speed_10m",
}
weather_result = weather.get(path="/forecast", params=weather_params)

print(f"weather_result:{weather_result}")
