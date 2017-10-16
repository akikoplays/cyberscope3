
var Trisha = function (_parent, _name){
    this.parent = _parent;
    this.sprite = null;
    this.name = _name;
    this.type = 'actor';
    this.direction = 1;
};

Trisha.prototype = {

    init: function(x, y) {
        this.sprite = game.add.sprite(x, y, 'trisha'); 
        this.sprite.animations.add('ugh', Phaser.ArrayUtils.numberArray(26, 26), 1, false);
        this.sprite.animations.add('dance', Phaser.ArrayUtils.numberArray(0, 8), 10, true);
        this.sprite.animations.play('dance');
        this.sprite.anchor.x = 0;
        this.sprite.anchor.y = 1.0;
        this.sprite.scale.x = 1.5;
        this.sprite.scale.y = 1.5;
    },

    update: function() {

    },

    hit: function(hitter) {
        this.sprite.filters = [this.parent.filter];
        var that = this;
        game.time.events.add(200, function() {
            that.sprite.filters = null;
        });

        var dir = hitter.sprite.x < this.sprite.x ? 1 : -1;
        game.add.tween(this.sprite).to({x:this.sprite.x+50*dir},80,Phaser.Easing.None,true);
        this.sprite.animations.play('ugh');
        this.sprite.scale.x = -dir * 1.5;
        game.time.events.add(600, function() {
            that.sprite.animations.play('dance');
        });
    },
};