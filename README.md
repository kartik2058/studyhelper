# StudyHelper
StudyHelper is an app server for an app that help students to help each other in studies. 

## Setting up the Server
To setup the StudyHelper server please follow the step given below

- First clone the StudyHelper server repository using ```git clone https://github.com/kartik2058/StudyHelper.git```
- Then go into the StudyHelper server directory using ```cd StudyHelper```
- Setup three environment variables using ```export variable_name = variable_value```
  - ```APP_SETTINGS``` variable, This variable can take two values ```config.DevelopmentConfig``` or ```config.ProductionConfig```. If you want the app to be in Debug mode then use DevelopmentConfig otherwise use ProductionConfig.
  - ```SECRET_KEY``` variable, This variable is used for security purpose if you are running the server in development environemnt then use any ```SECRET_KEY```
  - ```DATABASE_URL``` variable, This variable takes the url of your database you can use any type of database like Postgres, MySQL etc. as long as it is supported in SQLAlchemy.
- Then run the ```database_setup.py``` script to setup (create all tables) for your database.
- You are now ready to run your server. Run ```python app.py``` to run the server.
- You can see the server live at ```localhost:5000``` or ```127.0.0.1:5000```

Thanks for using StudyHelper Server.
