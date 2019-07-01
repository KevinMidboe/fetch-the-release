const fs = require('fs')

const whoAmI = (result) => {
  return `${result.title} (${result.year}) - ${result.status}`
}

const printAll = (media) => {
  media.forEach(item => {
    console.log(whoAmI(item))
  })
}

const writeCache = async (releases) => {
  console.log(releases)
  return new Promise((resolve, reject) => {
    fs.writeFile('./releases.cache', JSON.stringify(releases), (err) => {
      if (err)
        return console.log(err)

      resolve()
      console.log('releases cache saved')
    })
  })
}

const readCache = () => {
  return Promise.resolve(fs.readFile('./releases.cache', 'utf-8', (err, data) => {
    if (err) throw err;
    console.log(data)
    return JSON.parse(data)
  }))
}

module.exports = { whoAmI, printAll, writeCache, readCache }
