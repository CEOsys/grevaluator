library(shiny)
# Define UI for random distribution app ----
ui <- fluidPage(
  titlePanel("Tabsets"),
  sidebarLayout(
    sidebarPanel(
      radioButtons(
        "dist", "Distribution type:",
        c(
          "Normal" = "norm",
          "Uniform" = "unif",
          "Log-normal" = "lnorm",
          "Exponential" = "exp"
        )
      ),
      br(),
      sliderInput("n",
        "Number of observations:",
        value = 500,
        min = 1,
        max = 1000
      )
    ),
    mainPanel(
      tabsetPanel(
        type = "tabs",
        tabPanel("Plot", plotOutput("plot")),
        tabPanel("Summary", verbatimTextOutput("summary")),
      )
    )
  )
)


# Define server logic for random distribution app ----
server <- function(input, output) {
  d <- reactive({
    dist <- switch(input$dist,
      norm = rnorm,
      unif = runif,
      rnorm
    )
    dist(input$n)
  })

  output$plot <- renderPlot({
    dist <- input$dist
    n <- input$n

    hist(d(),
      main = paste("r", dist, "(", n, ")", sep = ""),
      col = "#75AADB", border = "white"
    )
  })

  # Generate a summary of the data ----
  output$summary <- renderPrint({
    summary(d())
  })
}

shinyApp(ui = ui, server = server)
