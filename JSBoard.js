// holds javascript scripts to alter the html game for javascript-powered play
function removeOnClickEvents() {
    console.log("removing onclickevents");
    done = false;
    for (y=0; y<1000; y++) {
        for (x=0; x<1000; x++) {
            try {
                tile = document.getElementById(x + ',' + y);
                tile.onclick = null;
                tile.classList.remove("link");
            } catch (error) {
                if (x == 0) {  // if first element has trouble, we're probably past the last row
                    done = true;
                }
                break;  // break out to move to next row
            }
        }
        if (done) {
            break;
        }
    }
}
function remove_links(args) {
    // this script runs immediately to remove html links, set up on-click events,
    console.log("removing links, setup onclicks");
    done = false;
    for (y=0; y<1000; y++) {
        for (x=0; x<1000; x++) {
            try {
                tile = document.getElementById(x + ',' + y);
                ahrefs = tile.getElementsByTagName("a");
                if (ahrefs.length >= 1) {
                    // we get here if we found an <a href>. Remove it because we want to use the tiles themselves.
                    a = ahrefs[0];
                    tile.classList.add("link"); // show pointer on tile
                    tile.removeChild(a);
                    tile.onclick = function() { clicked(this) };
                }
            } catch (error) {
                if (x == 0) {  // if first element has trouble, we're probably past the last row
                    done = true;
                }
                break;  // break out to move to next row
            }
        }
        if (done) {
            break;
        }
    }
}
remove_links([]);
function set_active_player(player_id) {
    // first remove "active" from all players. ID starts at player_1
    console.log("setting active player: " + player_id);
    for (ID=1; ID<100; ID++) {
        try {
            player = document.getElementById("player_" + ID);
            player.classList.remove("active");  // remove "active" setting from player
        } catch (error) {
            break;
        }
    }
    // set active player
    player = document.getElementById(player_id);
    player.classList.add("active");
}
set_tile_turn = 'window.is_tile_turn = true;'
set_move_turn = 'window.is_tile_turn = false;'
// this script runs immediately when html page is loaded
// and query the server to determine setup (who's turn it is, type of turn, etc)
var statusXhr = new XMLHttpRequest();
statusXhr.open("POST", "/js/on_load_setup/", true);
statusXhr.onload = function() {
    console.log(this.responseText);
    console.log(this.responseURL);
    var data = JSON.parse(this.responseText);
    console.log(data);
    function callFunction(functionName) {
        //JSON data contains arguments for function to call, key is the function name
        func = window[functionName];  // get function object
        args = data[functionName];    // get arguments for function
        if (func != null && args != null) {
            func(args);   // call function (example: "move_player")
        }
    }
    //callFunction("set_active_player");  // gets active player ID and sets it
}
statusXhr.send();
function remove_tile(tile_ids) {
    for (let tile_id of tile_ids) {
        console.log("removing tile: " + tile_id);
        var tile = document.getElementById(tile_id);
        tile.opacity = 0;
        var tile_interval = setInterval(frame_dissolve, 5);
        opacity = 1;
        function frame_dissolve() {
            if (opacity <= 0) {
                // tile fully removed
                clearInterval(tile_interval);
                tile.style.opacity = 0;
                tile.classList.remove("visible");
                tile.classList.add("hidden");
            } else {
                // decrease opacity
                opacity -= 0.05;
                tile.style.opacity = opacity;
            }
        }
    }
}
function change_turn(args) {
    // DO NOT use is_tile_turn != is_tile_turn because we don't initialize tile_turn in beginning
    if (window.is_tile_turn == true) {
        window.is_tile_turn = false;
        console.log("change to player-move turn");
    } else {
        window.is_tile_turn = true;
        console.log("change to tile-remove turn");
    }
}
function link_tiles(tile_ids) {
    // if no tile_ids supplied, will just remove all links
    remove_links([]);
    removeOnClickEvents();
    for (let tile_id of tile_ids) {
        tile = document.getElementById(tile_id);
        tile.onclick = function() { clicked(this) };
    }
}
function clicked(element) {
    console.log("clicked " + element.id);
    var xhr = new XMLHttpRequest();
    if (window.is_tile_turn == true) {
        xhr.open("POST", "/js/remove_at/" + element.id, true);
    } else {
        // default to moving to a tile, since window.is_tile_turn can be null
        xhr.open("POST", "/js/move_to/" + element.id, true);
    }
    xhr.onload = function() {
        console.log("POST response:");
        console.log(this.responseText);
        console.log(this.responseURL);
        var data = JSON.parse(this.responseText);
        console.log(data);
        function callFunction(functionName) {
            //JSON data contains arguments for function to call, key is the function name
            func = window[functionName];  // get function object
            args = data[functionName];    // get arguments for function
            if (func != null && args != null) {
                func(args);   // call function (example: "move_player")
            }
        }
        callFunction("move_player") // MOVE PLAYER if applicable
        callFunction("remove_tile") // REMOVE TILE if applicable
        callFunction("change_turn") // change turn
        callFunction("link_tiles")  // change which tiles are linked
    }
    xhr.send();
}
// animate movement to next tile
function move_player(args) {
    // moves player to same position as tile, animated
    // if window is scrolled, this animation will be offset from it's desired location
    [player_id, tile_id] = args;
    player = document.getElementById(player_id);
    tile = document.getElementById(tile_id);
    p_rect = player.getBoundingClientRect();
    x1 = p_rect.left;
    y1 = p_rect.top;
    t_rect = tile.getBoundingClientRect();
    x2 = t_rect.left;
    y2 = t_rect.top;
    // we have to remove player from being within a div tile
    // in order for it to appear above other elements. zIndex did not help
    document.body.append(player);
    // reset coordinates, or it'll snap to edge of body
    player.style.left = x1;
    player.style.top = y1;  
    // animate movement
    var interval = setInterval(frame, 5);
    function frame() {
        if (x1 == x2 && y1 == y2) {
            // player finished moving
            clearInterval(interval);
        } else {
            // set magnitude
            xmag = Math.abs(x2 - x1);
            xsign = (x2 - x1)/xmag;  // get -1 or 1 depending on which way x should go
            ymag = Math.abs(y2 - y1);
            ysign = (y2 - y1)/ymag;  // get -1 or 1 depending on which way y should go
            // move one pixel at a time towards other tile
            x1 += xsign;
            y1 += ysign;
            player.style.left = x1;
            player.style.top = y1;
        }
    }
}

