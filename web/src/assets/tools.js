

export function ParseSeconds(second){
    console.log(second)
    if (second == null) return null

    const totalSec = Math.floor(Math.abs(second))

    const hours = Math.floor(totalSec / 3600)
    const min = Math.floor((totalSec % 3600) / 60)
    const seconds = totalSec - ((hours * 3600) + (min*60))

    return `${String(hours).padStart(2,'0')}:${String(min).padStart(2,'0')}:${String(seconds).padStart(2,'0')}`


}

export function formatDate(timestamp) {return new Date(timestamp * 1000).toLocaleDateString();}
