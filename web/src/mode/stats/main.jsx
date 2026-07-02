import BG from "../../components/Background";
import "../../index.css"
import { BarChart, Tooltip, XAxis, Cell, Pie, PieChart } from "recharts";
import { motion } from "framer-motion";
import { FaCoins, FaGem, FaClock, FaInfinity, FaChartLine, FaCalendarAlt, FaArrowLeft } from "react-icons/fa";
import { FiTarget } from "react-icons/fi";
import { GiSwordClash, GiCompass } from "react-icons/gi"
import { useState, useEffect } from "react";
import api from "../../api/index"
import { formatDate, ParseSeconds } from "../../assets/tools";
import { useNavigate } from "react-router-dom"
import { CartoonButton } from "../../components/assets"


function StatCard({ children, title, color, icon = null, delay }) {

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: delay }}
      className={`bg-linear-to-br ${color} rounded-3xl p-5 shadow-hard border-2 border-white/30 flex flex-col items-center text-center`}
    >
      <div className="text-4xl mb-2 text-white drop-shadow">{icon}</div>
      <div className="text-4xl font-black text-white">{children}</div>
      <div className="text-lg font-bold text-white/80 mt-1">{title}</div>
    </motion.div>
  )
}

function LastGameTable({ data }) {

  return (
    <div className="bg-black/40 backdrop-blur-md rounded-3xl p-6 shadow-hard border border-white/20">

      <h2 className="text-2xl font-bold text-white flex items-center gap-2 mb-6"><FaCalendarAlt /> Dernières parties</h2>

      <table className="w-full text-white">
        <thead className="border-b border-white/20">
          <tr>
            <th className="text-left py-2 px-4">Mode</th>
            <th className="text-left py-2 px-4">Résultat</th>
            <th className="text-left py-2 px-4">Essais</th>
            <th className="text-left py-2 px-4">Date</th>
          </tr>
        </thead>
        <tbody>
          {data.map((session) => (
            <tr key={session.id} className="border-b border-white/10 hover:bg-white/10 transition">
              <td className="py-2 px-4">
                {session.type === "classic" && <FiTarget className="inline mr-1" />}
                {session.type === "discovery" && <GiCompass className="inline mr-1" />}
                {session.type === "level" && <GiSwordClash className="inline mr-1" />}
                {session.type}
              </td>
              <td className="py-2 px-4">
                {session.result === "won" ? (
                  <span className="text-green-400">Victoire</span>
                ) :
                  session.result === "lose" ? (
                    <span className="text-red-400">Défaite</span>
                  ) : (<span className="text-yellow-400">Abandone</span>)

                }
              </td>
              <td className="py-2 px-4">{session.attemps ?? "-"}</td>
              <td className="py-2 px-4">{formatDate(session.date)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}


export default function stats() {
  const navigate = useNavigate()
  const [player, setPlayer] = useState({ name: null, id: null, coins: null, gems: null, xp: null, level: null })
  const [stats, setStats] = useState({
    fatestWin: null, TotalTime: null,
    TotalTries: null, meanTries: null, TotalGames: null, endedGames: null, winGames: null
  })

  const WinRateColors = ["#4ade80", "#f87171", "#e1fd0b"];

  const [winRateData, setWinRateData] = useState([])
  const [historyGame, setHistoryGame] = useState([])



  useEffect(() => {
    setWinRateData([
      { name: "Gagne", value: stats.winGames },
      { name: "Perdu", value: stats.endedGames - stats.winGames },
      { name: "Abandone", value: stats.TotalGames - stats.endedGames }
    ])
  }, [stats])





  useEffect(() => {
    const fetchAllData = async () => {
      const player_id = localStorage.getItem("id");

      const [playerData, statsData, historyData] = await Promise.all([
        api.get(`/user/${player_id}`),
        api.get(`/user/stats/${player_id}`),
        api.get(`/user/stats/history/${player_id}`)
      ]);
      setPlayer(playerData);
      setStats(statsData);
      setHistoryGame(historyData);

    };

    fetchAllData();
  }, []);



  return (
    <>
      <BG />
      <div>

        <div className="flex justify-start p-1">
          <CartoonButton className="text-3xl p-2 " onClick={() => navigate("/")}>
            <div className="flex items-center justify-center"><FaArrowLeft /><div>Retour</div></div></CartoonButton>
        </div>

        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="backdrop-blur-xl border-4 border-yellow-400 rounded-3xl p-4 shadow-[0_0_20px_rgba(250,204,21,0.15)] relative overflow-hidden"
        >

          <div className="flex flex-col md:flex-row items-center  gap-6 relative z-10">
            {/* Avatar */}
            <div className="w-16 h-16 bg-slate-700 rounded-2xl border-2 border-white flex items-center justify-center text-4xl font-game font-black text-yellow-400 shadow-inner">
              {player.name?.[0] || "null"}
            </div>

            {/* Info Joueur */}
            <div className="flex-1 text-center md:text-left">
              <div className="flex items-center justify-center md:justify-start gap-2 mb-1">
                <h1 className="text-3xl font-bold text-amber-50 italic tracking-tight">
                  {player.name ?? "..."}
                </h1>
                <span className="bg-yellow-400 text-black text-xs font-bold px-2 py-0.5 rounded uppercase">
                  Niv. {player.level ?? "..."}
                </span>
              </div>

              {/* Barre XP */}
              <div className="w-full max-w-md bg-slate-950 h-4 rounded-full overflow-hidden border border-slate-600 relative">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${(player.xp / (player.level + 1) * 1000) * 100}%` }}
                  transition={{ duration: 1, ease: "easeOut" }}
                  className="h-full bg-linear-to-r from-yellow-500 to-orange-500"
                />
                <span className="absolute inset-0 flex items-center justify-center text-[10px] font-bold text-white/80 mix-blend-overlay">
                  XP {player.xp} / {(player.level + 1) * 1000}
                </span>
              </div>
            </div>

            {/* Wallet */}
            <div className="flex gap-4">
              <div className="bg-slate-950/80 border-2 border-slate-600 px-4 py-2 rounded-xl flex items-center gap-3">
                <FaCoins className="text-yellow-400 text-xl" />
                <span className="font-game font-bold text-lg">{player.coins ?? "..."}</span>
              </div>
              <div className="bg-slate-950/80 border-2 border-slate-600 px-4 py-2 rounded-xl flex items-center gap-3">
                <FaGem className="text-cyan-400 text-xl" />
                <span className="font-game font-bold text-lg">{player.gems ?? "..."}</span>
              </div>
            </div>
          </div>
        </motion.div>


        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 p-4">
          <StatCard title="victoire la plus rapide" icon={<FaClock />} color="from-purple-500 to-pink-600" delay={0.4} >{stats.fatestWin ? stats.fatestWin.toFixed(2) : <FaInfinity />}s</StatCard>
          <StatCard title="Temps total passé" icon={<FaClock />} color="from-red-500 to-red-600" delay={0.4} >{ParseSeconds(stats.TotalTime) ?? <FaInfinity />}</StatCard>
          <StatCard title="Temps total d'essais" icon={<FaClock />} color="from-slate-500 to-slate-600" delay={0.4} >{stats.TotalTries ?? <FaInfinity />}</StatCard>
          <StatCard title="Nombre d'essais Moyen" icon={<FaClock />} color="from-green-500 to-green-600" delay={0.4} >{stats.meanTries ?? <FaInfinity />}</StatCard>
        </div>

        <div className="flex gap-1 p-1">
          <div className="bg-black/20 items-center backdrop-blur-md rounded-3xl p-2 shadow-hard border border-white/20">
            <h2 className="text-2xl font-bold text-white flex items-center gap-2 mb-4"><FaChartLine /> Taux de victoire</h2>
            <PieChart width={250} height={250}>
              <Pie data={winRateData} cx="50%" cy="50%" innerRadius={60} outerRadius={90} fill="#8884d8" dataKey="value" nameKey={"name"}>
                {winRateData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={WinRateColors[index % WinRateColors.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value, name) => [`${value} (${((value / stats.TotalGames) * 100).toFixed(1)}%)`, name]} />

            </PieChart>
          </div>
          <div className="flex-1">
            <LastGameTable data={historyGame} />
          </div>
        </div>
      </div>



    </>

  )

}