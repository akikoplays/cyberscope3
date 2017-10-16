
var Player = function (_parent, _name){
    this.parent = _parent;
    this.sprite = null;
    this.name = _name;
    this.type = 'actor';
    this.direction = 1;
};

Player.prototype = {

    init: function(x, y) {
        console.log("Initing player..");
        // main character
        this.sprite = game.add.sprite(x, y, 'trisha');
        this.sprite.animations.add('walk', Phaser.ArrayUtils.numberArray(9,14), 12, false);
        this.sprite.animations.add('whip', Phaser.ArrayUtils.numberArray(68,73), 12, false);
        this.sprite.animations.add('dance', Phaser.ArrayUtils.numberArray(0, 8), 10, false);
        this.sprite.anchor.x = 0.5;
        this.sprite.anchor.y = 1.0;
        this.sprite.scale.x = 1.5;
        this.sprite.scale.y = 1.5;
        this.sprite.filters = null;

        this.anim = this.sprite.animations.play("dance");
        // game.physics.enable(sprite, Phaser.Physics.ARCADE);
    },

    update: function() {
            var flags = 0;
            if (game.input.keyboard.isDown(Phaser.Keyboard.LEFT))
                flags |= 1;
            if (game.input.keyboard.isDown(Phaser.Keyboard.RIGHT))
                flags |= 1 << 1;
            if (game.input.keyboard.isDown(Phaser.Keyboard.DOWN))
                flags |= 1 << 2;
            if (game.input.keyboard.isDown(Phaser.Keyboard.UP))
                flags |= 1 << 3;
            if (game.input.keyboard.isDown(Phaser.Keyboard.SPACEBAR)) {
                if (this.anim && this.anim.name != 'whip') {
                    this.sprite.animations.stop();
                    this.anim = this.sprite.animations.play('whip');
                    //this.sprite.filters = [this.filter];
                }
            }

            if (this.anim.name == 'whip') {
                if (!this.anim.isFinished) {
                    flags = 0;
                }
                else {

                    // eval hit
                    var actors = this.parent.objs['actors'];
                    for (key in actors) {
                        var ga = actors[key];
                        if (ga == this)
                            continue;
                        if (this.parent.isActorOverlapped(ga)) {
                            ga.sprite.filters = [this.parent.filter];
                        }
                    }

                    this.anim = this.sprite.animations.play('walk');
                    this.anim.stop();
                    this.sprite.filters = null;
                }
            } else if (this.anim.name == 'walk') {
                if (this.anim.isFinished)
                    this.anim.stop();
            }

            if (flags & 1) {
                if (this.sprite.animations.getAnimation('walk').isPlaying == false)
                            this.anim = this.sprite.animations.play('walk');

                this.sprite.x -= speed;
                if (this.sprite.scale.x == 1.5)
                    this.sprite.scale.x = -1.5
                this.direction = -1;
            } 
            if (flags & (1 << 1)) {
                if (this.sprite.animations.getAnimation('walk').isPlaying == false)
                            this.anim = this.sprite.animations.play('walk');
                this.sprite.x += speed;
                if (this.sprite.scale.x == -1.5)
                    this.sprite.scale.x = 1.5
                this.direction = 1;
            }
            if (flags & (1 << 2)) {
                this.sprite.animations.play('walk');
                this.sprite.y += speed;
            }
            if (flags & (1 << 3)) {
                this.anim = this.sprite.animations.play('walk');
                this.sprite.y -= speed;
            } 

            if (this.sprite.x < 0) 
                this.sprite.x = 0;
            if (this.sprite.x > this.parent.objs['city1'].width - 40) 
                this.sprite.x = this.parent.objs['city1'].width - 40;
            if (this.sprite.y < 530) this.sprite.y = 530;
            if (this.sprite.y > 600) this.sprite.y = 600;

    },

};