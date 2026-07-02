import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom";
import { FaLock } from "react-icons/fa";
import { AnimatePresence, motion } from "framer-motion";
import useGameSound from "../../hooks/SoundHooks";
import { CartoonButton } from "../../components/assets";

const shakeVariants = {
  idle: { x: 0 },
  left: { x: [0, -12, 10, -8, 6, -4, 0], transition: { duration: 0.45 } },
  right: { x: [0, 12, -10, 8, -6, 4, 0], transition: { duration: 0.45 } },
};

const slideVariants = {
  enter: (direction) => ({
    x: direction > 0 ? 300 : -300,
    opacity: 0,
  }),
  center: {
    x: 0,
    opacity: 1,
    transition: { duration: 0.4, ease: "easeOut" },
  },
  exit: (direction) => ({
    x: direction < 0 ? 300 : -300,
    opacity: 0,
    transition: { duration: 0.3, ease: "easeIn" },
  }),
};

export default function LevelSelect({ player, onSelect }) {
  const [currentPage, setCurrentPage] = useState(1);
  const levelsPerPage = 20;
  const [visibleLevels, setVisibleLevels] = useState([]);
  const navigate = useNavigate()
  const [shake, setShake] = useState(null);
  const [direction, setDirection] = useState(0); // 1 = next, -1 = prev
  const { inGameSound } = useGameSound()


  useEffect(() => {
    const start = (currentPage - 1) * levelsPerPage + 1;
    const end = currentPage * levelsPerPage;
    const newLevels = [];
    for (let i = start; i <= end; i++) {
      newLevels.push(i);
    }
    setVisibleLevels(newLevels);
  }, [currentPage]);


  const next = () => {
    setDirection(1)
    setCurrentPage((prev) => prev + 1);
  };

  const prev = () => {
    setDirection(-1)
    if (currentPage == 1) { setShake("right"); setTimeout(() => setShake(null), 500); return; }

    setCurrentPage((prev) => prev - 1);
  };

  useEffect(() => {
    const handleKey = (e) => {
      if (e.key === "ArrowRight") next();
      if (e.key === "ArrowLeft") prev();
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [currentPage]);

  function LvlBtn({ level, isLock }) {

    function HandleClick(){
      if (!isLock) { onSelect(level);inGameSound.click() }
      else {inGameSound.notallowedclick()}
    }

    return (
      <div className={`border-4  rounded-2xl shadow-3d-button flex text-2xl text-amber-50 font-black flex-col justify-center items-center
      ${isLock ? "bg-[#0000004d] border-[#ffffff12] cursor-not-allowed" : "bg-[#3b82f638] hover:-translate-y-1  hover:bg-cartoon-blue transition-all hover:shadow-3d-button-hov border-gray-500 duration-300 cursor-pointer"}
      `}
        onClick={HandleClick}>

        {isLock ? <FaLock /> : null}
        {level}
        <span className="text-white/30 text-[10px]">1-{level * 10}</span>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-screen relative">
      <div className="relative z-10 flex flex-col h-full p-3">

        <div className="flex justify-between">
          <div className="text-3xl font-black text-amber-400">NIVEAUX</div>
          <div className="text-white font-bold text-xs">// utilise les touches directionnelles pour changer de page</div>
        </div>

        <motion.div
          className="flex-1 overflow-hidden mt-2 "
          variants={shakeVariants}
          animate={shake ?? "idle"}
        >
          <AnimatePresence mode="wait" custom={direction}>
            <motion.div
              key={currentPage}
              className="grid h-full sm:grid-cols-5 gap-3 backdrop-blur-sm rounded-xl p-3 bg-white/20  "
              variants={slideVariants}
              custom={direction}
              exit="exit"
              initial="enter"
              animate="center">

              {visibleLevels.map((e, k) => {
                const unlocked = e <= player.level
                return (<LvlBtn level={e} isLock={!unlocked} />)
              })}

            </motion.div>
          </AnimatePresence>
        </motion.div>

        <div className="flex justify-center">
        <CartoonButton className="h-10 w-[60%] mt-3" 
        onClick={()=>navigate("/")}>
          Retour à l'ecran de jeu</CartoonButton>
        </div>

      </div>
    </div>)
}

