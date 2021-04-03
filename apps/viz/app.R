library(shiny)
library(ggplot2)
library(shinythemes)
library(DT)
library(eeptools)
library(tidyverse)
library(dplyr)
library(RCurl)
library(jsonlite)

content <- getURL("http://viz-backend:80/patient/get/F00000787", .opts = list(followlocation = TRUE, ssl.verifyhost = FALSE, ssl.verifypeer = FALSE))
data <- fromJSON(content)
data <- do.call(rbind, data) %>%
  as.data.frame() %>%
  t() %>%
  as.data.frame()

pats <- getURL("http://viz-backend:80/patient/list/", .opts = list(followlocation = TRUE, ssl.verifyhost = FALSE, ssl.verifypeer = FALSE))
patlist <- fromJSON(pats)
patlist <- do.call(rbind, data) %>%
  as.data.frame() %>%
  t() %>%
  as.data.frame()

## LL-Url: (Titel, Text, Variablen in P[], I[]) für jede LL


## setwd("C:/Users/bienertt/OneDrive - Charite - Universitaetsmedizin Berlin/RCodes")
load("hosplist_simple.Rdata")

# as.Date(as.POSIXct)
patdat$Alter <- floor(age_calc(as.Date(patdat$DOB), units = "years"))
patdat$ITSTag <- as.numeric(floor(age_calc(as.Date(patdat$ITSStart), units = "days")))
new_adm <- as.numeric(floor(age_calc(as.Date(as.character(patlist[patlist$variable_name == "admission_hospitalisation", ]$value)), units = "days")))

tabldspl <- data.frame(
  "Name" = c(patdat$Name, c(as.character(unique(patlist$pseudo_fallnr)))),
  "Alter" = c(patdat$Alter, ""),
  "ITSTag" = c(patdat$ITSTag, new_adm),
  "P" = rep(TRUE, 7),
  "I" = c(rep(c(TRUE, FALSE), 3), FALSE),
  "PIerf" = c("")
)

LL <- data.frame(
  choices <- c("Intervention I bei Population P", "Dexamethason bei kritisch kranken Patienten mit COVID-19"),
  text <- c(
    "LL fuer I bei P\n mit sehr viel langem test-text TEST TEST TEST TEST TEST \n TEST TEST",
    "Hier steht der LL-Text zu SAD bei Covid-19"
  ),
  lllink <- c("www.google.de", "www.wikipedia.de")
)

# Create Fluidpage with User Interface
ui <- fluidPage(
  themeSelector(),
  theme = shinytheme("united"),
  # Left Column
  column(
    3,
    fluidRow(
      # Stationsauswahl und CEOSys/NUM-Logo
      column(3, img(src = "logo_num.jpg", height = 50), align = "center"),
      column(3, img(src = "logo_ceosys.jpg", height = 50), align = "center"),
      column(6, selectInput(
        inputId = "ward", label = "Station",
        choices = c("ALL", patdat$Ward),
        selected = patdat$Ward[1],
        width = "80%"
      ),
      align = "center"
      )
    ),
    hr(),
    fluidRow(
      # Patiententabelle
      DT::dataTableOutput("x11"),
      verbatimTextOutput("y11")
    )
  ),
  # Right Column
  column(
    9,
    # Toprow: Leitlinienauswahl
    fluidRow(
      column(
        12,
        selectInput(
          inputId = "LLsel", label = "Leitlinien",
          choices = LL$choices,
          selected = NULL,
          width = "100%"
        ),
      )
    ),
    hr(),
    # 2nd Row: Leitlinien Infotext
    fluidRow(
      column(
        12,
        verbatimTextOutput("verb"),
        tags$head(tags$style("#verb{font-size:12px; font-style:italic;overflow-y:scroll; max-height: 20%; background: ghostwhite;}")),
        uiOutput("lllink")
      )
    ),
    # 3rd Row: Information zur Population
    hr(),
    fluidRow(
      column(
        12,
        titlePanel("Population"),
        wellPanel(uiOutput("out_mainpopu"))
      )
    ),
    # 4th Row: Information zur Intervention
    hr(),
    fluidRow(
      column(
        12,
        titlePanel("Intervention"),
        sidebarLayout(
          sidebarPanel(
            uiOutput("out_sideintv")
          ),
          mainPanel(wellPanel(
            textOutput("out_mainintv")
          ))
        )
      )
    )
  )
)


############# Server ############
server <- function(input, output, session) {

  # Functions for left column
  rward <- reactive({
    input$ward
  })

  # Patient data table
  options(DT.options = list(pageLength = 20))
  observeEvent(rward(), {
    if (input$ward == "ALL") {
      tabldat <- tabldspl
    }
    else {
      tabldat <- tabldspl[patdat$Ward == rward(), ]
    }

    output$x11 <- DT::renderDataTable(
      server = FALSE,
      DT::datatable(tabldat,
        rownames = FALSE,
        selection = "single",
        colnames = c("Name", "Alter", "ITS-Tag ", "P", "I", "P&I erfüllt")
      ) %>% formatStyle(c(4:6),
        backgroundColor = styleEqual(
          c(TRUE, FALSE),
          c(
            rgb(200, 230, 200, 255, 255, 255),
            rgb(230, 200, 200, 255, 255, 255)
          )
        )
      )
    )
    output$y11 <- renderPrint(cat(c("Pat. ", tabldat[input$x11_rows_selected, ]$Name, " selected.")))
  })


  ##### Functions for right column #####
  output$verb <- renderText({
    LL[LL$choices == input$LLsel, ]$text
  })
  output$lllink <- renderUI({
    LL[LL$choices == input$LLsel, ]$lllink
  })

  observeEvent(input$LLsel, {
    print(LL[LL$choices == input$LLsel, ]$lllink)

    if (LL$choices[2] == input$LLsel) {
      # Diese Informationen werden zukünftig direkt durch LL-Endpoint definiert
      popu <- c(as.character(unique(data$variable_name)))[!grepl("drug", variables, fixed = TRUE)]
      intv <- "Dexamethason"
    }
    else {
      popu <- c("Population 1", "Population 2")
      intv <- c("Intervention 1", "Intervention 2")
    }

    ## Population Row
    #     plotInput <- reactive({
    #       n_plot <- length(popu[1:2])
    #       total_data <- lapply(1:n_plot, function(i){rnorm(500)})
    #       return (list("n_plot"=n_plot, "total_data"=total_data))
    #     })
    # ## Create divs ##
    #     output$out_mainpopu <- renderUI({
    #       plot_output_list <- lapply(1:plotInput()$n_plot, function(i) {
    #         plotname <- paste0("plot_", i)
    #         plotOutput(plotname, height = 280, width = 250)
    #       })
    #       do.call(tagList, plot_output_list)
    #     })
    #
    #     observe({
    #       lapply(1:plotInput()$n_plot, function(i){
    #         output[[paste("plot", i, sep="") ]] <- renderPlot({
    #           hist(plotInput()$total_data[[i]], main = paste("Histogram Nr", i))
    #         })
    #       })
    #     })

    ## Intervention Row
    output$out_sideintv <- renderUI({
      checkboxGroupInput("chk_sideintv", " ", intv)
    })
    output$out_mainintv <- renderText({
      "Schoene Informationen"
    })
  })

  # observeEvent(input$LLsel, {
  #   output$out_plotpopu <- renderPlot({
  #
  #     lbl_top <- "RASS"
  #     x_top <- as.POSIXct(as.character(data[data$variable_name==lbl_top,]$datetime))
  #     y_top <- as.numeric(data[data$variable_name==lbl_top,]$value)
  #
  #     lbl_mid <- "SOFA"
  #     x_mid <- as.POSIXct(as.character(data[data$variable_name==lbl_mid,]$datetime))
  #     y_mid <- as.numeric(data[data$variable_name==lbl_mid,]$value)
  #
  #     if(LL$choices[1]==input$LLsel){
  #       x_btm <- c(1:100)
  #       y_btm <- x_btm*sin(x_btm)
  #       #Bottom
  #       par(fig=c(0, 1, 0, 0.4),new=TRUE, mar = c(2,2,2,2))
  #       plot(x_btm, y_btm, xlab="",ylab="")
  #       abline(v = x_btm[ceiling(length(x_btm)/3)], untf = FALSE)
  #       text(x_btm[ceiling(length(x_btm)/3)],y_btm[ceiling(length(x_btm)/3)]+.1*ceiling(length(x_btm)/3),"   Medi1",adj = c(0,0))
  #     }
  #     if(LL$choices[2]==input$LLsel){
  #       #Bottom
  #       par(fig=c(0, 1, 0, 0.4),new=TRUE, mar = c(2,2,2,2))
  #       plot(x_mid, y_mid, xlab="Time",ylab="")
  #       grid()
  #       #Top
  #       par(fig=c(0, 1, .6, 1),new=TRUE, mar = c(2,2,2,2))
  #       plot(x_top,y_top,ylab=lbl_top,xlab=" ",ylim = c(-5,4))
  #       grid()
  #
  #       par(fig=c(0.9, 1, .6, 1),new=TRUE, mar = c(2,0,2,0))
  #       boxplot(y_top, axes=FALSE)
  #
  #       #Mid
  #       par(fig=c(0 , 1, .3, .7), new=TRUE, mar = c(2,2,2,2))
  #       plot(x_mid, y_mid, ylab=lbl_mid,xlab=" ")
  #       grid()
  #
  #       par(fig=c(0.9, 1, .3, .7),new=TRUE, mar = c(2,0,2,0))
  #       boxplot(y_mid, axes=FALSE)
  #     }
  #
  #   })
  # })
}

shinyApp(ui = ui, server = server)
