/*var EventsState = function (game){
};

EventsState.prototype = {
    init: function() {
    },
    create: function() {
    },
    preload: function() {
    },
    update: function() {
    }
};
*/

var EventsState = function (game){
    this.objs = [];
};

EventsState.prototype = {
    init: function() {
    },

    create: function() {

        var that = this;

        // We need some gfx (black rect) to use for fading screen in and out, or tinting elements
        let black = game.add.graphics(0,0);
        black.visible = false;
        black.beginFill(0x000000);
        black.alpha = 1;
        black.drawRect(0, 0,
            game.width, game.height);
        black.endFill();

        this.objs.black = black;


        // Set up event sync manager
        this.mgr = new EventManager(this);

        // events are organized as trees, there is the root event, to which you can attach n-children
        // this structure affects relative events time, e.g. root event 1 starts at 2 seconds, it's 1st child starts 
        // at 2.5 seconds and 2nd at 6 seconds (local time), menaing in root event's time 1st child will start at 2+2.5s 
        // and 2nd child at 2+6s. If those children have children their time will be also counted locally, starting at 0
        // and added to their parent's times. Similar to OGL Matrix concatenations :)
        let rootEvent = new Event("root", 1.0, function(evt, root){console.log("I am excited!")});

        let e = new Event("fadein", 2.0, function(evt, root){
            root.objs.black.visible = true;
            let tween = game.add.tween(root.objs.black).to({alpha:0},1000,Phaser.Easing.None,true);
            tween.onComplete.add(function() {
                console.log("### Tween over");
            });
        });
        rootEvent.addEvent(e);

        // finally add the tree to manager
        this.mgr.addEvent(rootEvent);
    },
    
    preload: function() {
    },
    
    update: function() {
        this.mgr.update();
    }
};


class Event {
    constructor(name, time, fn) {
        this.mgr = null;
        this.time = time;
        this.fn = fn;
        this.state = "pending";
        this.children = [];
        this.parent = null;
        this.name = name;
        this.startRTC = 0;
    }

    activate() {
        this.startRTC = game.time.totalElapsedSeconds();
        // let child = null;
        // for (i=0; i<this.children.length; i++) {
        //     child = this.children[i];
        //     child.activate();
        // }
        for (var child of this.children) {
            child.activate();
        }
    }

    getRoot() {
        if (this.parent)
            return this.parent.getRoot();
        else 
            return this;
    }

    fire() {
        this.state = "running";
        this.fn(this, this.getRoot().getManager().getRoot());
    }

    update() {
        let time = game.time.totalElapsedSeconds();
        if (this.state == "pending") {
            if (time - this.startRTC >= this.time) {
                this.fire();
            }
        }

        for (var child of this.children) {
            child.update();
        }

    }

    stop() {
        this.state = "stopped";
    }

    getManager() {
        return this.mgr;
    }

    // Add event to an event, it behaves like a child. 
    addEvent(evt) {
        evt.mgr = this.mgr;
        evt.parent = this;
        this.children.push(evt);
    }

}

class EventManager {
    constructor(root /*this gamestate instance == root*/) {
        this.root = root;
        this.totalTime = 0;
        this.events = [];
    }

    addEvent(evt) {
        evt.mgr = this;
        this.events.push(evt);
    }

    getRoot() {
        return this.root;
    }

    update() {
        // let time = this.getCurTime();
        for (var event of this.events) {
            event.update();
        }
    }
}

