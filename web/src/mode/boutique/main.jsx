import Props from "../../components/PlayerProps"
import { useState, useEffect } from "react"
import api from "../../api"
import ShopCard from "./ShopCard"
import BG from "../../components/Background"
import power_ups from "../../assets/Powerup"
import { motion, AnimatePresence } from "framer-motion";
import ShopCategory from "./ShopCategory";
import powerUp from "../../assets/Powerup"
import useGameSound from "../../hooks/SoundHooks"
import useInventory from "../../hooks/useInventory"


export default function Shop() {
    const [player, setPlayer] = useState({ name: null, id: null, coins: 0, gems: 0, xp: 0, level: 0 });
    const [activeCategory, setActiveCategory] = useState("hint");
    const [notification, setNotification] = useState(null);
    const {situationSound} = useGameSound()
    const { items: inventory, refresh: refreshInventory } = useInventory(player.id)

    useEffect(() => {
        const fetchData = async () => {
            const playerId = localStorage.getItem("id");

            const [playerData] = await Promise.all([
                api.get(`/user/${playerId}`),
            ]);
            setPlayer(playerData);

        };
        fetchData();
    }, []);

    // Fonction d'achat
    const handleBuy = async (item) => {
        const price = item.price;
        const currency = item.currency;
        const playerFunds = currency === "coin" ? player.coins : player.gems;
        if (playerFunds < price) {
            setNotification({ type: "error", message: `Pas assez de ${currency === "coin" ? "pièces" : "gemmes"} !` });
            setTimeout(() => setNotification(null), 2000);
            return;
        }

        try {
            const res = await api.post("/shop/buy", {
                playerId: player.id,
                itemId: item.id,
            });
            setPlayer(res);
            refreshInventory()
            situationSound.onBuy()
            setNotification({ type: "success", message: `${item.name} acheté !` });
            setTimeout(() => setNotification(null), 2000);
        } catch (error) {
            console.error(error);
            setNotification({ type: "error", message: error.message || "Erreur lors de l'achat" });
            setTimeout(() => setNotification(null), 2000);
        }
    };

    const filteredItems = powerUp.filter(item => item.category === activeCategory);


    return (
        <>
            <BG />
            <div className="relative z-10 flex flex-col h-dvh w-full overflow-auto ">
                <Props coins={player.coins} gems={player.gems} xp={player.xp} name={player.name} mode={"shop"} />

                <div className="flex-1 px-6">
                    <ShopCategory active={activeCategory} onSelect={setActiveCategory} />

                    {/* Grille d'items */}
                    <motion.div

                        className="grid lg:grid-cols-3 xl:grid-cols-4 gap-6 mt-8 w-full max-w-7xl mx-auto"
                    >
                        <AnimatePresence>
                            {filteredItems.map((item) => (
                                <motion.div
                                    key={item.id}
                                    layout
                                    initial={{ opacity: 0, scale: 0.8 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    exit={{ opacity: 0, scale: 0.8 }}
                                    transition={{ duration: 0.2 }}
                                >
                                    <ShopCard
                                        item={item}
                                        isAffordable={item.price <= player.coins}
                                        owned={inventory[item.id] ?? 0}
                                        // quantity={inventory[item.id] || 0}
                                        onBuy={() => handleBuy(item)}
                                    // disabled={
                                    //     (item.currency === "coin" && player.coins < item.price) ||
                                    //     (item.currency === "gem" && player.gems < item.price)
                                    // }
                                    />
                                </motion.div>
                            ))}
                        </AnimatePresence>
                    </motion.div>
                </div>

                {/* Notification toast */}
                <AnimatePresence>
                    {notification && (
                        <div className="flex absolute bottom-8 w-full overflow-hidden justify-center">
                            <motion.div
                                initial={{ opacity: 0, y: 50 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: 50 }}
                                className={`flex   bg-amber-300  px-6 py-3 rounded-full font-bold text-white shadow-hard z-50 bg-green-500" 
                                }`}
                            >
                                {notification.message}
                            </motion.div>
                        </div>
                    )}
                </AnimatePresence>
            </div>
        </>
    );
}