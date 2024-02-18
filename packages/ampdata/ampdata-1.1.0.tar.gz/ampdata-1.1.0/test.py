import wapi

# Create a new client
session = wapi.Session(config_file="config.ini")

# Get curve
curve = session.get_curve(name="pri cz power spot eur/mwh cet h a")
data = curve.get_data(data_from="2019-01-01", data_to="2019-01-02")
print(data.to_pandas())
