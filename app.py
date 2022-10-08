from blog_site import create_app

app = create_app()

if __name__ == "__main__":
    app = create_app()
    # app.debug = True
    app.run(debug=True)






