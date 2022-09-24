<?php
    $error = "";
    if(isset($_POST["nachname"]) && !empty($_POST["nachname"])) {
        // create JSON object for python
        $personal = array();
        $personal["Name, Vorname"] = $_POST["nachname"] . ", " . $_POST["vornamen"];
        $geburtsdatum = implode(".", array_reverse(explode("-", $_POST["geburtsdatum"])));
        $personal["Geburtsdatum \(dd"] = array("mm" => array("yyyy\)" => $geburtsdatum));
        $personal["Vertragslaufzeit"] = $_POST["startmonat"].".".$_POST["startjahr"]." - ".$_POST["endmonat"].".".$_POST["endjahr"];
        $personal["Personalnummer"] = $_POST["personalnummer"];
        $personal["Kostenstelle"] = $_POST["kostenstelle"];
        $personal["Vorgesetzte:r"] = $_POST["vorgesetzte:r"];
        $personal["Struktureinheit"] = $_POST["struktureinheit"];
        $personal["Vereinbarte Wochenarbeitszeit"] = str_replace(",", ".", $_POST["wochenstunden"]);

        $worktime = array();
        $gesamtstunden = 0;
        for($i = 0; $i < 5; $i++) {
            $zeit = str_replace(",", ".", $_POST["arbeitszeit_".$i]);
            $zeit_zahl = floatval($zeit);
            $gesamtstunden += $zeit_zahl;
            $stunden = floor($zeit_zahl);
            $minuten = floor(60.0 * ($zeit_zahl - $stunden));

            $startzeit = explode(":", $_POST["startzeit_".$i]);
            $startminuten = intval($startzeit[1]);
            $startstunden = intval($startzeit[0]);
            $endminuten = ($startminuten + $minuten) % 60;
            $stundenüberlauf = ($startminuten + $minuten >= 60) ? 1 : 0;
            $endstunden = ($startstunden + $stunden + $stundenüberlauf) % 24;

            $worktime[$i] = array();
            $worktime[$i]["arbeitszeit"] = $zeit;
            $worktime[$i]["startzeit"] = $_POST["startzeit_".$i];
            // add to start time!!!
            $worktime[$i]["endzeit"] = sprintf("%02d", $endstunden).":".sprintf("%02d", $endminuten);
        }
        $fillmonth = explode("-", $_POST["month"]);
        $month = array("year" => $fillmonth[0], "month" => $fillmonth[1]);

        if($gesamtstunden == floatval($personal["Vereinbarte Wochenarbeitszeit"])) {
            $json = json_encode(array("personal" => $personal, "worktime" => $worktime, "month" => $month));
            $escapedjson = str_replace('"', '\"', $json);

            // execute python file
            // $ret = system("python3 script.py " . $json, $output);
            if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
                $output = shell_exec("python script.py \"" . $escapedjson . "\"");
            } else {
                $output = shell_exec("python script_python2.py '" . $json . "'");

            }
            $filename = trim($output) . ".pdf";

            // download finished pdf
            if(file_exists($filename)) {
                header('Content-Description: File Transfer');
                header('Content-Type: application/octet-stream');
                header('Expires: 0');
                header('Content-Disposition: attachment; filename="' . basename($filename) . '"');
                header('Content-Length: ' . filesize($filename));
                header('Pragma: public'); //?

                flush();
                readfile($filename);

                // delete pdf
                unlink($filename);

                die();
            }
        } else {
            $error = "Mehr Stunden gearbeitet als angegeben.";
        }
    }
?>
<!DOCTYPE html>
<html lang="de">
    <head>
        <title>SHK - Ausfüllen</title>
        <link rel="stylesheet" href="style.css">
        <script src="script.js" defer></script>
    </head>
    <body>
        <a id="downloadAnchorElem" style="display:none;"></a>

        <form name="form" method="post">
            <?php
                if($error != "") {
                    echo '<div class="error">';
                    echo $error;
                    echo '</div>';
                }
            ?>
            <h2>SHK - Arbeitszeitnachweis</h2>

            <h3>
                Persönliche Daten hochladen oder ausfüllen
                (<a onclick="toggle_personal()" id="unfold_personal">ausklappen</a>)
            </h3>
            <input type="file" name="personal_info" id="personal_info" style="width:auto">
            <!-- document.getElementById('spacing').classList.toggle('no_display') -->
            <div style="border-bottom:2px solid #525252;"></div>

            <div id="personal" class="no_display" style="border-bottom:2px solid #525252;">
                <div class="field" style="margin-top:2em">
                    <input type="text" name="nachname" id="nachname" placeholder=" " required>
                    <label for="nachname" class="animate">Nachname</label>
                </div>
                <div class="field">
                    <input type="text" name="vornamen" id="vornamen" placeholder=" " required>
                    <label for="vornamen" class="animate">Vorname(n)</label>
                </div>
                <div class="field">
                    <input type="date" name="geburtsdatum" id="geburtsdatum" placeholder=" " required>
                    <label for="geburtsdatum" class="animate">Geburtsdatum</label>
                </div>
                <div class="field">
                    <input type="text" name="personalnummer" id="personalnummer" pattern="[0-9]+" placeholder=" " required>
                    <label for="personalnummer" class="animate">Personalnummer</label>
                </div>
                <div class="field">
                    <input type="text" name="kostenstelle" id="kostenstelle" placeholder=" " required>
                    <label for="kostenstelle" class="animate">Kostenstelle</label>
                </div>
                <div class="field">
                    <input type="text" name="vorgesetzte:r" id="vorgesetzte:r" placeholder=" " required>
                    <label for="vorgesetzte:r" class="animate">Vorgesetzte:r</label>
                </div>
                <div class="field">
                    <input type="text" name="struktureinheit" id="struktureinheit" placeholder=" " required>
                    <label for="struktureinheit" class="animate">Struktureinheit</label>
                </div>
                <div>
                    <label class="inline">Vertragsbeginn</label>
                    <div style="display:flex; width:100%; gap:10px; margin-bottom:15px;">
                        <select name="startmonat" id="startmonat">
                            <?php
                                for($i = 1; $i <= 12; $i++) {
                                    echo "<option>$i</option>";
                                }
                            ?>
                        </select>
                        <select name="startjahr" id="startjahr">
                            <?php
                                $year = date("Y");
                                echo "<option>" . ($year + 1) . "</option>";
                                echo "<option selected>$year</option>";
                                echo "<option>" . ($year - 1) . "</option>";
                            ?>
                        </select>
                    </div>
                </div>
                <div>
                    <label class="inline">Vertragsende</label>
                    <div style="display:flex; width:100%; gap:10px;">
                        <select name="endmonat" id="endmonat">
                            <?php
                                for($i = 1; $i <= 12; $i++) {
                                    echo "<option>$i</option>";
                                }
                            ?>
                        </select>
                        <select name="endjahr" id="endjahr">
                            <?php
                                $year = date("Y");
                                echo "<option>" . ($year + 1) . "</option>";
                                echo "<option selected>$year</option>";
                                echo "<option>" . ($year - 1) . "</option>";
                            ?>
                        </select>
                    </div>
                </div>
                <div class="field">
                    <input type="text" name="wochenstunden" id="wochenstunden" pattern="[0-9]+[.,][0-9]" placeholder=" " required>
                    <label for="wochenstunden" class="animate">Vereinbarte Wochenarbeitszeit</label>
                </div>
                <button type="button" style="margin-bottom:10px" onclick="download_personal()">Daten herunterladen</button>
            </div>

            <h3>
                Zeit pro Tag hochladen oder ausfüllen
                (<a onclick="toggle_timePerDay()" id="unfold_timePerDay">ausklappen</a>)
            </h3>
            <input type="file" name="timePerDay_info" id="timePerDay_info" style="width:auto">
            <div style="border-bottom:2px solid #525252;"></div>

            <div id="timePerDay" class="no_display" style="border-bottom:2px solid #525252;">
                <div style="margin-bottom:.75em"></div>
                <button type="button" onclick="autofill_timePerDay()">Wöchentliche Arbeitszeit gleichmäßig aufteilen</button>
                <div style="margin-bottom:.75em"></div>
                <table>
                    <tr>
                        <th scope="col">Tag</th>
                        <th scope="col">Startzeit</th>
                        <th scope="col">Arbeitsstunden</th>
                    </tr>
                    <?php
                        $days = array("Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag");
                        for($i = 0; $i < 5; $i++) {
                            echo "<tr>";
                            echo "<th scope='row'>$days[$i]</th>";
                            echo "<td><input type='time' name='startzeit_$i' id='startzeit_$i' value='08:00'></td>";
                            echo "<td><input type='text' name='arbeitszeit_$i' id='arbeitszeit_$i' pattern='[0-9]+[.,][0-9]' value='0,0'></td>";
                            echo "</tr>";
                        }
                    ?>
                </table>
                <div style="margin-bottom:.75em"></div>
                <button type="button" onclick="download_timePerDay()">Daten herunterladen</button>
                <div style="margin-bottom:.75em"></div>
            </div>

            <div style="margin-top:.3em">
                <label for="month" class="inline">Monat</label>
                <select name="month" id="month">
                    <?php
                        $months = array("Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember");
                        $month = date("n") - 1;
                        $year = date("Y");
                        $begin = ($month - 5) % 12;
                        $end = ($month + 5) % 12;
                        $i = $begin;
                        while($i != $month) {
                            echo "<option value='" . (($i > $month) ? $year + 1 : $year) . "-" . ($i + 1) . "'>" . $months[$i] . "</option>"; // maybe $year - 1?
                            $i = ($i + 1) % 12;
                        }
                        echo "<option selected value='" . $year . "-" . ($month + 1) . "'>" . $months[$month] . "</option>";
                        $i = ($i + 1) % 12;
                        while($i - 1 != $end) {
                            echo "<option value='" . (($i < $month) ? $year + 1 : $year) . "-" . ($i + 1) . "'>" . $months[$i] . "</option>";
                            $i = ($i + 1) % 12;
                        }
                    ?>
                </select>
            </div>
            <div style="margin-bottom:1em"></div>
            <button type="submit">Formular Ausfüllen</button>
        </form>
    </body>
</html>