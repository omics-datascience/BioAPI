from bioapi import app
if __name__ == "__main__":
	port = int(os.environ.get('PORT', conf["server"]["port"]))
	app.run(host='localhost', port=port)
