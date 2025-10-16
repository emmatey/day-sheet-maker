  export function filterError(err){
    let error_str = err.message
    let detected = false;
    let buffer = [];

    for (let char of error_str) {
      if (buffer.length < 4){
        buffer.push(char);
      }

      if (buffer.length === 4 && detected === false){
         buffer.shift();
         buffer.push(char);
      }

      if (detected === true){
        buffer.push(char);
      }

      if (buffer.join("") === ("Err:")){
        detected = true;
      }
      
      if (detected === true && char === "'"){
        buffer.pop();
        break;
      }  

      if (detected === true && char === "\""){
        buffer.pop();
        break;
      } 
    }
      let filtered_error = buffer.join("");
      return filtered_error;
  };