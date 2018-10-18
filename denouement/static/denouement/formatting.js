// Used for formatting stuff that doesn't apply to an entire line
function formatLine(line, charToFind)
{
    let matchCount = 0;
    let tag;

    for (let charIndex in line)
    {

        if (charToFind == "*")
        {
            tag = "em";
        }

        if (charToFind == "**")
        {
            tag = "strong";
        }

        // We've dealt with a pair, reset
        if (matchCount == 2)
        {
            matchCount = 0;
        }

        if (matchCount == 0)
        {
            line = line.replace(charToFind,  "<" + tag + ">");
        }
        else if (matchCount == 1)
        {
            line = line.replace(charToFind, "</" + tag + ">");
        }

        matchCount++;
    }

    return line;
}

window.addEventListener("load", function()
{
    let allPostText = document.getElementsByClassName("post-text");

    for (let post of allPostText)
    {
        let text = post.innerHTML;
        post.innerHTML = "";
        
        text = text.split("\n");

        text.forEach(function(line, index)
        {
            if (line == "")
            {
                post.innerHTML += "<br>";
                return;
            }

            if (line.startsWith("# "))
            {
                line = line.replace("# " , "")
                post.innerHTML += "<h1>" + line + "</h1>";
                return;
            }   

            if (line.startsWith("## "))
            {
                line = line.replace("## " , "")
                post.innerHTML += "<h2>" + line + "</h2>";
                return;
            }

            line = formatLine(line, "**");
            line = formatLine(line, "*");

            post.innerHTML += line + "<br>";
        })
    }
})