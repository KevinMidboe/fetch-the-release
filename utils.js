
const whoAmI = (result) => {
  return `${result.title} (${result.year}) - ${result.status}`
}

const printAll = (media) => {
  media.forEach(item => {
    console.log(whoAmI(item))
  })
}

module.exports = { whoAmI, printAll }
