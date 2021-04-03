library(shiny)
library(ggplot2)
library(shinythemes)
# setwd("C:/Users/bienertt/OneDrive - Charité - Universitätsmedizin Berlin/RCodes")
load("hosplist_all.Rdata")

t <- c(1:100)
hf <- 70 / 60
abp <- data.frame("t" = t, "abp" = 100 * (sin(t / (hf * 10)) * .3 + 1))
rass <- data.frame("t" = c(1:10), "rass" = floor(runif(10, min = -5, max = 6)))
nrs <- data.frame("t" = c(1:10), "nrs" = floor(runif(10, min = -1, max = 11)))
camicu <- data.frame("t" = c(1:10), "camicu" = floor(runif(10, min = 0, max = 10)))


# Create Fluidpage with User Interface
ui <- fluidPage(
  theme = shinytheme("united"),
  fluidRow(
    column(3, selectInput(
      inputId = "hosp", label = "Krankenhaus",
      choices = unique(patdat$Hospital),
      selected = patdat$Hospital[1]
    )),
    column(2, selectInput(
      inputId = "ward", label = "Station",
      choices = NULL
    )),
    column(3, selectInput(
      inputId = "pat", label = "Patient",
      choices = NULL
    )),
    column(2, img(src = "logo_ceosys.jpg", height = 70), " ", img(src = "logo_num.jpg", height = 70, align = "right"))
  ),
  hr(),
  fluidRow(
    column(4, htmlOutput("patInfo")),
    column(7, htmlOutput("patInfo2")),
    column(1, "Bettplatz 1 Fenster")
  ),
  hr(),
  fluidRow(
    column(2, uiOutput("submenu")),
    column(
      10, # uiOutput("tabs"))
      tabsetPanel(
        id = "sys",
        tabPanel(title = "Akut", value = "akut", "test"),
        tabPanel(title = "Anamnese", value = "anamnese", "Anamnese mit zusaetzlichen Informationen"),
        tabPanel(title = "ZNS", value = "zns", plotOutput("grtop"))
      )
    )
  )
)

############# Server ############
server <- function(input, output, session) {
  rhosp <- reactive({
    input$hosp
  })
  observeEvent(rhosp(), {
    choices <- unique(patdat[patdat$Hospital == rhosp(), ]$Ward)
    updateSelectInput(inputId = "ward", choices = choices)
  })

  rward <- reactive({
    input$ward
  })
  observeEvent(rward(), {
    choices <- unique(patdat[patdat$Hospital == rhosp() & patdat$Ward == rward(), ]$Name)
    updateSelectInput(inputId = "pat", choices = choices)
  })

  output$patInfo <- renderUI({
    HTML("<table>
  <tr><p style=font-size:2em><strong>", input$pat, "</strong></p><tr/>
  <thead>
    <tr>
      <th scope=col> *19.07.1987 </th>
    </tr>
  </thead>
</table>")
  })

  output$patInfo2 <- renderUI({
    HTML("<table>
  <thead>
    <tr>
      <th scope=col>Date of Birth      </th>
      <th scope=col>PIZ                </th>
      <th scope=col>Allergien          </th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td> *19.07.1987                 </td>
      <td> 12345678###                 </td>
      <td> Graeser, Pollen, Atemluft   </td>
    </tr>
    <tr>
      <th scope=col>Date of Birth      </th>
      <th scope=col>PIZ                </th>
      <th scope=col>Allergien          </th>
    </tr>
    <tr>
      <td>1974              </td>
      <td>17                </td>
      <td>No More Heroes    </td>
    </tr>
  </tbody>
</table>")
  })

  output$logo_ceosys <- renderImage(
    {
      list(
        src = "logo_ceosys.jpg",
        filetype = "image/jpeg",
        height = 80,
        alt = "ceoSys"
      )
    },
    deleteFile = FALSE
  )
  output$logo_num <- renderImage(
    {
      list(
        src = "logo_num.jpg",
        filetype = "image/jpeg",
        height = 80,
        alt = "NUM"
      )
    },
    deleteFile = FALSE
  )

  observeEvent(input$sys, {
    print(input$sys)
    output$submenu <- renderUI({
      if (input$sys == "zns") {
        options <- c("NADiag" = "nad", "NeuroStatus" = "ns", "SDA" = "sda")
      }
      else {
        options <- c("A" = "a", "B" = "b", "C" = "c", "D" = "d", "E" = "e")
      }
      radioButtons("submenu", label = NULL, options)
    })
  })

  observeEvent(input$sys, {
    output$grtop <- renderPlot({
      varx_top <- camicu$t
      vary_top <- camicu$camicu

      varx_mid <- abp$t
      vary_mid <- abp$abp

      if (input$sys == "zns") {
        varx_btm <- rass$t
        vary_btm <- rass$rass
        # Bottom
        par(fig = c(0, 1, 0, 0.5), new = TRUE)
        plot(varx_btm, vary_btm, xlab = "Time", ylab = "RASS")
        abline(v = varx_btm[ceiling(length(varx_btm) / 3)], untf = FALSE)
        text(varx_btm[ceiling(length(varx_btm) / 3)], vary_btm[ceiling(length(varx_btm) / 3)] + .1 * ceiling(length(varx_btm) / 3), "  Medi1", adj = c(0, 0))
      }
      if (input$sys == "zns" & input$submenu == "ns") {
        # Bottom
        par(fig = c(0, 1, 0, 0.5), new = TRUE)
        plot(varx_mid, vary_mid, xlab = "Time", ylab = "pO2")
      }
      # Top
      par(fig = c(0, 1, .5, 1), new = TRUE)
      plot(varx_top, vary_top, xlab = "", ylab = "CAM-ICU")

      # Mid
      par(fig = c(0, 1, .25, .75), new = TRUE)
      plot(varx_mid, vary_mid, xlab = "", ylab = "ABP / mmHg")

      par(fig = c(0, 0.2, .25, .75), new = TRUE)
      boxplot(vary_mid, axes = FALSE)
    })
  })
}

shinyApp(ui = ui, server = server)
