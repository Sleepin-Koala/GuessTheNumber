import { motion } from "framer-motion";
import {AiFillThunderbolt} from "react-icons/ai"

const categories = [
  { id: "bonus", label: "Bonus" },
  { id: "hint", label: "Indices", },
  { id: "help", label: "Aide"},
];

export default function ShopCategory({ active, onSelect }) {
  return (
    <div className="flex justify-center gap-4 flex-wrap">
      {categories.map((cat) => (
        <motion.button
          key={cat.id}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => onSelect(cat.id)}
          className={`px-6 py-2 rounded-full font-bold text-lg transition-all ${
            active === cat.id
              ? "bg-yellow-400 text-black shadow-hard border-2 border-white"
              : "bg-white/20 text-white border border-white/30 hover:bg-white/30"
          }`}
        >
          {cat.label}
        </motion.button>
      ))}
    </div>
  );
}