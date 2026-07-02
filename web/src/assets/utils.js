
export function isSoundEnabled(){
    if (localStorage.getItem("sound") === "true") return true
    else return false
}

export function setSound(b){
    localStorage.setItem("sound" , b)
}

