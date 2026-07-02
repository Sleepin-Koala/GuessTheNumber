import { Howl } from "howler";


export class MainSound {

    constructor(){
        this.currentMusic = null
    }

    start(src , loop = false){
        this.currentMusic = new Howl({
            src: src,
            loop : loop
        })
        console.log(this.currentMusic)

        this.currentMusic.play()
    }

    stop(){
        console.log(this.currentMusic)
        if (this.currentMusic) this.currentMusic.stop();
        this.currentMusic = null
        console.log(this.currentMusic)

    }

}

export class SFX {

    constructor(){
        this.currentMusic = null
    }

    start(src , loop = false){
        this.currentMusic = new Howl({
            src: src,
            loop : loop
        })
        console.log(this.currentMusic)

        this.currentMusic.play()
    }

    stop(){
        console.log(this.currentMusic)
        if (this.currentMusic) this.currentMusic.stop();
        this.currentMusic = null
        console.log(this.currentMusic)

    }

}

export default [new MainSound() , new SFX()]