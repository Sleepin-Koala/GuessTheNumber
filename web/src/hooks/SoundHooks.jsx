import useSound from "use-sound";
import clickSfx from '../sounds/click.wav';

export default function useGameSound() {


    const [playClick] = useSound(clickSfx, { volume: 1 });
    const [playNotAllowed] = useSound("src/sounds/not_allowed.mp3", { volume: 1 });
    const [onFalseAnswer] = useSound("src/sounds/not.mp3", { volume: 1 });

    const [Win] = useSound("./src/sounds/win.wav", { volume: 1 });
    const [playBuy] = useSound("./src/sounds/buy.mp3", { volume: 1 });
    const [FailBuying] = useSound("./src/sounds/fail.mp3", { volume: 1 });
    const [BgMusic , {stop: stopBgMusic}] = useSound("./src/sounds/main.mp3", { volume: 1 });


    return {
        inGameSound: { click: playClick , notallowedclick : playNotAllowed , isFalse: onFalseAnswer ,
            onLose : FailBuying , onWin : Win
        },
        mainMusic : {play : BgMusic , stop : stopBgMusic},
        situationSound: { onBuy : playBuy }
    }

}

