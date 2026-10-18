import { useNavigate } from "react-router-dom";
import BG from "../../components/Background";
import { CartoonButton } from "../../components/assets";

// Le mode Duel n'est pas encore disponible dans la version web.
export default function Duel() {
    const navigate = useNavigate()

    return (
        <>
            <BG />
            <main className="relative z-10 flex flex-col items-center justify-center gap-6 min-h-dvh p-6 text-center">
                <h1 className="text-3xl sm:text-5xl font-black text-white drop-shadow-lg">Mode Duel</h1>
                <p className="text-white/80 text-lg">Bientôt disponible.</p>
                <CartoonButton className="min-h-11 px-6" onClick={() => navigate("/")}>Retour</CartoonButton>
            </main>
        </>
    )
}
