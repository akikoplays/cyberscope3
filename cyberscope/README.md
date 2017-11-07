# Insipiration: 

https://youtu.be/LTRZcIwRg5A?t=979
let it scroll babe.. 


# Some useful sources:

* https://github.com/photonstorm/phaser-coding-tips/blob/master/issue-008/aliens.html
* https://jsfiddle.net/BinaryMoon/a68Qp/


# Sprite tools:

* configuration for Shoebox support for Phaser tex atlas: https://github.com/netcell/PhaserShoeBoxConfig

	Sublime tips:
	To convert new lines to \n i used regex box, and wrote find: (\n) replace \n.
	To remove single \n characters and keep \n\n i used this regex: (^|[^\\n])\\n(?!\\n)


# GitHub pages for this project:

https://akikoplays.github.io/cyberscope3/cyberscope/cyber.html


# Coding take-aways from this project

While working on this project I learned couple of things, here they are :)

	// to add a fade out to an object use tween:
    tween = game.add.tween(that.objs['articles']).to({alpha:0.0},1000,Phaser.Easing.Cubic.Out,true);

    // to call a function after tween is complete:
    tween.onComplete.add(function(){...});

    // to call a function after some time:
    game.time.events.add(3000, function() {...});


