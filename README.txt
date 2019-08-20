A websocket server for hosting games that can be played in a browser.

Flow:

Client                                                      Server
Establishes Websocket Connection    ------------------------->
Checks for user-id cookie ----------------------------------->
Checks if cookie has valid user id --------------------------> Checks if id exists
Doesn't exist <-----------------------------------------------
Sends Username and Game code --------------------------------> Validates and adds user to games
     <-------------------------------------------------------- Sends user-id back
Sets userid cookie
Plays Game.