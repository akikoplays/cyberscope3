/* ======================== BootState ==============================*/
/*  loads starting screen, shows some blitter image fx and gives control
    to the content table of contents */

var text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quid ergo aliud intellegetur nisi uti ne quae pars naturae neglegatur? Si longus, levis; Ita relinquet duas, de quibus etiam atque etiam consideret. Optime, inquam. Sed quanta sit alias, nunc tantum possitne esse tanta.\nQuid, si etiam iucunda memoria est praeteritorum malorum? Consequatur summas voluptates non modo parvo, sed per me nihilo, si potest; Atque his de rebus et splendida est eorum et illustris oratio. Mihi enim satis est, ipsis non satis. Ergo ita: non posse honeste vivi, nisi honeste vivatur? Mihi quidem Antiochum, quem audis, satis belle videris attendere. Et quod est munus, quod opus sapientiae? Ex rebus enim timiditas, non ex vocabulis nascitur. Ex ea difficultate illae fallaciloquae, ut ait Accius, malitiae natae sunt. Nonne videmus quanta perturbatio rerum omnium consequatur, quanta confusio? Quae cum magnifice primo dici viderentur, considerata minus probabantur.";

var IntroState = function (game){
    this.bmpTitle = null;
    this.bmpBlockLeft = null;
    this.bmpBlockRight = null;
    this.objs = [];
};

const TITLE_Y = 100;
const TEXT_Y = 130;
const TEXT_X = 20;
const TEXT_BLOCK_SPACE = 20;
const TEXT_BLOCK_WIDTH = 350;
const LEFT_BLOCK_X = TEXT_X;
const RIGHT_BLOCK_X = TEXT_X + TEXT_BLOCK_WIDTH + TEXT_BLOCK_SPACE;

IntroState.prototype = {

    init: function() {

    },

    preload: function() {
        this.game.load.image('171', 'assets/171.png');
        this.game.load.image('imgHeader', 'assets/header.png');
        this.game.load.image('imgFooter', 'assets/footer.png');
        this.game.load.bitmapFont('gem', 'assets/gem.png', 'assets/gem.xml');
        this.game.load.json('contents', 'assets/contents.json');
    },

    create: function() {
        this.game.stage.backgroundColor = "#200000";
        this.game.stage.smoothed = false;

        json = this.game.cache.getJSON('contents');
        console.log(json);
        title = json.articles[0].title;
        text = json.articles[0].body;

        y = TEXT_Y;
        x = TEXT_X;
        width = TEXT_BLOCK_WIDTH;
        space = TEXT_BLOCK_SPACE;
        size = 16;

        this.objs['titleFont'] = this.game.add.retroFont('171', 16, 18, "ABCDEFGHIJKLMNOPQRSTUVWXYZ| 0123456789*=!ø:.,\\?->=:;+()`", 19, 0, 1);
        //this.objs['titleFont'].setText("ABOUT CYBERSCOPE 3", true, 0, 8, Phaser.RetroFont.ALIGN_CENTER);
        this.objs['titleSprite'] = game.add.image(LEFT_BLOCK_X, TITLE_Y, this.objs['titleFont']);
        this.objs['titleFont'].text = title;
        this.objs['titleSprite'].x = -this.objs['titleSprite'].width;
        //this.bmpTitle = game.add.bitmapText(-200, TITLE_Y, 'gem', 'About Cyberscope 3', size);
        //this.bmpTitle.tint = 0xaabbff;


        this.bmpBlockLeft = game.add.bitmapText(game.width, y, 'gem', "loading", size);
        this.bmpBlockLeft.tint = 0xeeddff;
        this.bmpBlockLeft.maxWidth = width;
        this.bmpBlockLeft.text = text;

        this.bmpBlockRight = game.add.bitmapText(game.width + RIGHT_BLOCK_X, y, 'gem', "loading", size);
        this.bmpBlockRight.tint = 0xeeddff;
        this.bmpBlockRight.maxWidth = width;
        this.bmpBlockRight.text = text;

        //console.log(this.bmpBlockRight.height);
        //console.log(this.bmpTitle.height);

        this.game.add.tween(this.objs['titleSprite']).to({x:LEFT_BLOCK_X},1000,Phaser.Easing.Cubic.Out,true);
        this.game.add.tween(this.bmpBlockLeft).to({x:LEFT_BLOCK_X},1000,Phaser.Easing.Cubic.Out,true);
        this.game.add.tween(this.bmpBlockRight).to({x:RIGHT_BLOCK_X},1000,Phaser.Easing.Cubic.Out,true);

        // add header and footer images
        this.objs['header'] = this.game.make.bitmapData();
        this.objs['header'].load('imgHeader');
        this.objs['footer'] = this.game.make.bitmapData();
        this.objs['footer'].load('imgFooter');
        this.objs['sHeader'] = this.game.add.sprite(0, -this.objs['footer'].height, this.objs['header']);
        this.objs['sFooter'] = this.game.add.sprite(0, game.height+this.objs['footer'].height, this.objs['footer']);
        this.game.add.tween(this.objs['sFooter']).to({y:game.height - this.objs['footer'].height},1000,Phaser.Easing.Cubic.Out,true);
        this.game.add.tween(this.objs['sHeader']).to({y:0},1000,Phaser.Easing.Cubic.Out,true);


    },


    update: function() {
        // Hack for passing the context of this to timeout fn
        var that = this;

    },

};
