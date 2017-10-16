
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
        this.sprite.animations.add('dance', Phaser.ArrayUtils.numberArray(0, 8), 10, true);
        this.sprite.animations.play('dance');
        this.sprite.anchor.x = 0;
        this.sprite.anchor.y = 1.0;
        this.sprite.scale.x = 1.5;
        this.sprite.scale.y = 1.5;
    },

    update: function() {

    },

};